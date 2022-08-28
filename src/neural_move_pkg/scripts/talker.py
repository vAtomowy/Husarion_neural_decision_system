#!/usr/bin/env python
# license removed for brevity
import rospy
import time
import neurolab as nl
import numpy as np
import math
from rospy.rostime import Duration
from std_msgs.msg import String
from enum import Enum
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import PoseStamped 


# Dane do uczenia 
x1 = np.array([1,1,1,1,0,0,0,0,0,1,1,1,1,1]);
print(x1);
x2 = np.array([1,0,1,0,0,1,0,1,0,1,1,0,0,1]);
print(x2);
x3 = np.array([0,0,0,0,0,1,1,1,1,1,1,1,1,1]);
print(x3);
x4 = np.array([1,1,0,0,0,1,1,0,0,1,0,1,0,1]);
print(x4);
x5 = np.array([1,1,1,1,0,1,1,1,1,0,0,0,0,1]);
print(x5);
y = np.array([0,0,0,0,0,-1,-1,-1,-1,1,1,1,1,0]);
print(y);

size_1 = len(x1);
size_2 = len(x2);
size_3 = len(x3);
size_4 = len(x4);
size_5 = len(x5);
size_y = len(y); 

inp_1 = x1.reshape(size_1,1);
inp_2 = x2.reshape(size_2,1);
inp_3 = x3.reshape(size_3,1);
inp_4 = x4.reshape(size_4,1);
inp_5 = x5.reshape(size_5,1);
INPT = np.hstack((inp_1,inp_2,inp_3,inp_4,inp_5));

tar = y.reshape(size_y,1);

net = nl.net.newff([[-1, 1],[-1, 1],[-1, 1],[-1, 1],[-1, 1]],[5, 1]);

print("Warstwa wejscia:",net.ci);
print("Warstwa wyjscia:",net.co);
print("Glebokosc warstw:",len(net.layers));

print(INPT);
print(tar);
# Train network
error = net.train(INPT, tar, epochs=500, show=100, goal=0.02)

# Simulate network
out = net.sim(INPT);

# Plot result
# import pylab as pl
# pl.subplot(211)
# pl.plot(error)
# pl.xlabel('Epoch number')
# pl.ylabel('error (default SSE)')

# F1 = np.array([[1, 1, 1, 1, 1]]);
# print(F1);
# y2 = net.sim(F1);
# print(y2);

# pl.subplot(212)
# pl.plot(F1, y2, '-');
# pl.legend(['train target', 'net output'])
# pl.show()

# while True:
#     print("Neural ok");

vel_msg = Twist(); 
p = PoseStamped(); 
zero = "0";

vel_msg.linear.x = 0;
vel_msg.linear.y = 0;
vel_msg.linear.z = 0;
vel_msg.angular.x = 0;
vel_msg.angular.y = 0;
vel_msg.angular.z = 0;

#odleglosci dla sprawdzanych katow 
class data:
    m90d = 0; 
    m45d = 0; 
    zerod = 0; 
    p45d = 0;
    p90d = 0;  
    m90dx = 0; 
    m45dx = 0; 
    zerodx = 0; 
    p45dx = 0;
    p90dx = 0; 

class action(Enum):
    stop = 0; 
    prosto  = 1;
    ukos_lewo = 2;
    lewo = 3;
    ukos_prawo = 4;
    prawo = 5;

class iter: 
    i = 0;
    m = 0;

def callback(msg):
    print("Ilosc probek");
    print(len(msg.ranges)) 
    print(" 90 stopni:");
    print(msg.ranges[1080]);
    data.p90d = msg.ranges[1081]; 
    print(" 45 stopni:"); 
    print(msg.ranges[1260]);
    data.p45d = msg.ranges[1260];
    print(" 0 stopni:"); 
    print(msg.ranges[0]);
    data.zerod = msg.ranges[0];
    print(" -45 stopni:"); 
    print(msg.ranges[180]);
    data.m45d = msg.ranges[180]
    print(" -90 stopni:"); 
    print(msg.ranges[360]);
    data.m90d = msg.ranges[359];

def callback_pose(msg2):
    # print("XXXXXXX:");
    # print(msg2.pose.position.x);
    # print("YYYYYYY:"); 
    # print(msg2.pose.position.y);
    p.pose.position.x = msg2.pose.position.x;
    p.pose.position.y = msg2.pose.position.y;

def call_action(action):

    if(action == 0):
        vel_msg.linear.x = 0;
        vel_msg.angular.z = 0.0;
    if(action == 1):
        vel_msg.linear.x = 0.15;
        vel_msg.angular.z = 0.0;
    if(action == 2):
        vel_msg.linear.x = 0.1;
        vel_msg.angular.z = -0.05;
    if(action == 3):
        vel_msg.linear.x = 0.14 #0.1;
        vel_msg.angular.z = -1.6 #-0.64;
    if(action == 4):
        vel_msg.linear.x = 0.1;
        vel_msg.angular.z = 0.05;
    if(action == 5):
        vel_msg.linear.x = 0.14;
        vel_msg.angular.z = 1.6;

def talker():

    #czekanie na inne procesy 
    rospy.sleep(7.);
    #publikacja wiadomosci 
    pub = rospy.Publisher('chatter', String, queue_size=10)
    #inicjalizacja tego wezla 
    rospy.init_node('talker', anonymous=True)
    sub = rospy.Subscriber('/scan', LaserScan, callback)
    sub2 = rospy.Subscriber('/pose', PoseStamped, callback_pose)
    # publikacja ruchu:
    velocity_publisher = rospy.Publisher('/cmd_vel', Twist, queue_size=10)

    rate = rospy.Rate(100) #100Hz

    # vel_msg.linear.x = 0;
    # vel_msg.linear.y = 0;
    # vel_msg.linear.z = 0;
    # vel_msg.angular.x = 0;
    # vel_msg.angular.y = 0;
    # vel_msg.angular.z = 0;
    # velocity_publisher.publish(vel_msg);

    # kasowanie plikow
    f3 = open("/home/husarion/logs/pose_feedback.txt", "w")
    f3.write(zero);
    f3.write("\t");
    f3.write(zero);
    f3.write("\n\r");
    f3.close();

    f2 = open("/home/husarion/logs/neural_data.txt", "w")
    f2.write(zero);
    f2.write("\n\r");
    f2.close();
        
    f = open("/home/husarion/logs/neural_feedback.txt", "w")
    f.write(zero);
    f.write("\n\r");
    f.close();

    while not rospy.is_shutdown():

        hello_str = "RosPyTime: %s" % rospy.get_time();
        rospy.loginfo(hello_str);
        pub.publish(hello_str);

        if((rospy.get_time())>(iter.i + 1)):
            #minela sekunda
            iter.m = iter.m+1;
        iter.i = rospy.get_time();
        # iter.i = iter.i+1;
        # if(iter.i > 99): 
        #     # minela sekunda
        #     iter.m = iter.m+1;
        #     iter.i = 0;
        if(iter.m > 8):
            # do 4 sekund
           iter.m = 0;
        print("WYBRANIE AKCJI !");

        # dzialanie sieci neuronowej - wybor akcji
        # wyswietlenie punktw z lidara  
        print(" -90 stopni:");
        print(data.m90d); 
        print(" -45 stopni:"); 
        print(data.m45d);
        print(" 0 stopni:"); 
        print(data.zerod);
        print(" 45 stopni:"); 
        print(data.p45d);
        print(" 90 stopni:"); 
        print(data.p90d);

        if(data.m90d == np.inf):
            data.m90d = data.m45d;
        if(data.m45d == np.inf):
            data.m45d = data.m90d;
        if(data.zerod == np.inf):
            data.zerod = 0.5;
        if(data.p90d == np.inf):
            data.p90d = data.p45d;
        if(data.p45d == np.inf):
            data.p45d = data.p90d;


        # if(data.m90d < 0.2):
        #     data.m90d = 0;
        # else:
        #     data.m90d = 1;
        # if(data.m45d < 0.2):
        #     data.m45d = 0;
        # else: 
        #     data.m45dx =1;
        # if(data.zerod < 0.2):
        #     data.zerodx = 0;
        # else: 
        #     data.zerodx = 1;
        # if(data.p90d < 0.2):
        #     data.p90dx = 0;
        # else: 
        #     data.p90dx = 1;
        # if(data.p45d < 0.2):
        #     data.p45dx = 0;
        # else:
        #     data.p45dx = 1;


        vec2 = np.array([[((data.m90d/1)),((data.m45d/1)),((data.zerod/1)), ((data.p45d/1)), ((data.p90d/1)) ]]);
        print("Zwrcone przez siec:");
        print(vec2); 
        out_3 = net.sim(vec2);
        print(out_3);
        
        x = str(p.pose.position.x);
        y = str(p.pose.position.y);

        f3 = open("/home/husarion/logs/pose_feedback.txt", "a");
        f3.write(x);
        f3.write("\t");
        f3.write(y);
        f3.write("\n\r");
        f3.close();

        f2 = open("/home/husarion/logs/neural_data.txt", "a");
        f2.write(str(vec2));
        f2.write("\n\r");
        f2.close();
        
        f = open("/home/husarion/logs/neural_feedback.txt", "a")
        f.write(str(out_3));
        f.write("\n\r");
        f.close();

        if(out_3 > [[0.5]]):
            print("JAZDA W LEWO !!!");
            call_action(5); 
            velocity_publisher.publish(vel_msg);
        if(out_3 < [[-0.5]]):
            print("JAZDA W PRAWO !!!");
            call_action(3);
            velocity_publisher.publish(vel_msg); 
        if(out_3 < [[0.5]] and out_3 > [[-0.5]]):
            print("JAZDA PROSTO !!!");
            call_action(1);
            velocity_publisher.publish(vel_msg);
        # if( (data.m90d < 0.15) and (data.zerod < 0.1) and (data.p90d < 0.15) ):
        #     print("STOP !!!");
        #     call_action(0);
        #     velocity_publisher.publish(vel_msg);

        #rospy.loginfo("x:%f y:%f ", feedback_pose.x, feedback_pose.y);
        
        #ter.m == 1: 
        #     vec = np.array([[0, 0, 0, 0, 0]]);
        #     # print("Zwrcone przez siec:");
        #     # print(vec); 
        #     out_2 = net.sim(vec);

        # if(iter.m > 1 and iter.m < 5):
        #     if(out_2 > 0.8): 
        #         # prawo 
        #         print("prawo");
        #         call_action(3); 
        #         velocity_publisher.publish(vel_msg);
        #     elif(out_2 < -0.8): 
        #         #lewo 
        #         print("lewo");
        #         call_action(5); 
        #         velocity_publisher.publish(vel_msg);
        #     elif((out_2 < 0.2) and (out_2 > -0.2)): 
        #         #prosto 
        #         print("prosto !")
        #         call_action(1); 
        #         velocity_publisher.publish(vel_msg); 

        # if((iter.m == 2) or (iter.m == 4) or (iter.m == 6) or (iter.m == 8)):
        #     call_action(0); 
        #     velocity_publisher.publish(vel_msg)
        # if iter.m == 3:
        #     call_action(1);
        #     velocity_publisher.publish(vel_msg)
        # if iter.m == 5:
        #     call_action(3);
        #     velocity_publisher.publish(vel_msg)
        # if iter.m == 7:
        #     call_action(5);
        #     velocity_publisher.publish(vel_msg)

        rate.sleep()
 
if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass


