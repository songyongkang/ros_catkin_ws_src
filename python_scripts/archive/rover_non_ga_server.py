"""
    Simple non-ga server for the basicbot.
"""
 
import json
import zmq
 
import random
 
import threading

random.seed(10)

Num_evaluation_workers = 2
 
class senderThread(threading.Thread):
    def __init__(self, threadID, socket, num_genomes=10):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.socket = socket
        self.num_genomes = num_genomes
 
    def run(self):
        print("Gnome - center_spin_thresh, center_drive_thresh, center_stop_thresh, stopping_thresh")
        print("\t\t\t\tStarting Sender Thread:"+str(self.threadID))
        self.send_data()
        print("\t\t\t\tExiting Sender Thread:"+str(self.threadID))
 
    def send_data(self):
        """ Send data to worker processes. 
 
        Args:
            socket: socket to send the data out on.
                - Persistant throughout execution for now.
        """
        #ind = {'id':0,'genome':[
        #            float("{0:.6f}".format(random.random()*10.0)), # center_spin_thresh
        #            float("{0:.6f}".format(9.0 + random.random() * 1.0)), # center_drive_thresh
        #            float("{0:.6f}".format(random.random()*10.0)), # center_stop_thresh
        #            float("{0:.6f}".format(random.random()*10.0)) # stopping_thresh
        #        ], 'fitness':-1.0}
        
        
        #ind = {'id':0,'genome':[
        #            float("{0:.6f}".format(5.7)), # center_spin_thresh
        #            float("{0:.6f}".format(9.4)), # center_drive_thresh
        #            float("{0:.6f}".format(5.8)), # center_stop_thresh
        #            float("{0:.6f}".format(2.06)) # stopping_thresh
        #        ], 'fitness':-1.0}
                
        
        ind = {'id':0,'genome':{
					'physical':[
                    {'sensor':'lidar', 'pos':[0,0,0.4], 'orient':[0,0,0]}
                    ],
                    'behavioral':[
                    {'test':0}
                    ]
                }, 'fitness':-1.0}
        
        for i in range(self.num_genomes/2+1):
            ind['id'] = i+50
            ind['genome']['behavioral'][0]['test'] = 0.4 + i * 0.1
            msg = json.dumps(ind)
            print(msg)
            socket.send(msg)
            
        for i in range(self.num_genomes/2+1,self.num_genomes):
            ind['id'] = i+50
            ind['genome']['physical'][0]['pos'][2] = 0.4 + i * 0.05
            msg = json.dumps(ind)
            print(msg)
            socket.send(msg)
            
        for i in range(Num_evaluation_workers):
            ind['id'] = -1
            print('Sending finish msg')
            msg = json.dumps(ind)
            socket.send(msg)
       
 
# Setup the socket to send data out on.
context = zmq.Context()
socket = context.socket(zmq.PUSH)
#socket.setsockopt(zmq.LINGER, 0)    # discard unsent messages on close

#socket.bind('tcp://35.9.28.201:5000')
socket.bind('tcp://127.0.0.1:5000')
 
# Setup the socket to read the responses on.
receiver = context.socket(zmq.PULL)
#receiver.bind('tcp://35.9.28.201:5010')
receiver.bind('tcp://127.0.0.1:5010')
 
print("Press Enter when the workers are ready: ")
_ = raw_input()
print("Sending tasks to workers")
 
# How many genomes to test sending
test_genome_num = 10

# Start a thread to send the data.
sendThread = senderThread(1, socket, num_genomes=test_genome_num)
sendThread.start()
 
# Read the responses on the receiver socket.
i = test_genome_num
while i > 0:
    data = json.loads(receiver.recv())
    print("Fitness: {}, Genome ID: {}, Host: {}".format(data['fitness'],data['id'],data['ns']))
    i -= 1
 
# Wait for the send thread to complete.
sendThread.join()
 
print("Closing Socket..")
socket.close()
receiver.close()
print("...Closed!")
print("Press Enter to close script: ")
_ = raw_input()
