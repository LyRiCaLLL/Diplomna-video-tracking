clc; clear all;close all;
t = tcpclient("192.168.1.162",5000);
t1 = 0;
br = 0;

index = 0;
vectorrecmsg = [];
pos_x = [];
pos_y = [];
vecVelY = [];
vecVelX = [];
vecArea = [];
posFrameLR = [];

resolution = [480, 640];
rosinit('192.168.1.144')
pub = rospublisher('/cmd_vel','geometry_msgs/Twist');
msg = rosmessage('geometry_msgs/Twist');
sub = rossubscriber('/odom');
while true
    index = index + 1;
    t1 = t.BytesAvailable;
    arr = [0,0,0,0];
    if t1 >= 4
        arr = read(t);
        br = br + 1;
        i = 1;
        join = [];
        if arr(length(arr)) == 1
           fin_val =  length(arr) - 1;
        else
            fin_val = length(arr);
        end
        arr;
        for i = 1:1:fin_val
            if i == length(arr)&& arr(i) ~=1
                join(i,1) = arr(i);
                join(i,2) = 0;
            else
                if arr(i) > 1 && arr(i+1) ~=1 && arr(i) ~= 1 || arr(i) == 1 && arr(i+1) == 1|| arr(i) == 0 && arr(i+1) == 1
                    join(i,1) = arr(i);
                    join(i,2) = 0;

                end
            end
            if i == length(arr)&& arr(i) ~=1
%            if arr(i) > 1
%                join(i,1) = arr(i);
%                join(i,2) = 255;    
           % end
            else
                if arr(i) > 1 && arr(i+1) == 1 || arr(i) == 1 && arr(i+1) == 1 || arr(i) == 0 && arr(i+1) == 1
                join(i,1) = arr(i);
                join(i,2) = 255; 

                end
            end
            if arr(i) == 1 && arr(i+1)>1
                join(i,1) = 0;
                join(i,2) = 0; 
            end
        end
        join;
        c = 1;
        fin = [];
        for j = 1:length(join)
            if join(j,1)~=0 || join(j, 2)~=0
                fin(c) = join(j,1)+join(j,2);
                c = c + 1;
                
            end
        end
        fin;
        x = fin(1);
        y = fin(2);
        w = fin(3);
        h = fin(4);
        area = w*h
        cx = x+(w/2);
        cy = y+(h/2);
        centerCam = resolution(2)/2;
        posFrameLR(index) = cx;
        if cx > centerCam + 30
            msg.Linear.Y = -.05; 
           % задавате скоростта по x
        %на дясно
        vecVelY(index) = -.05;
        elseif cx < centerCam - 30
            msg.Linear.Y = .05; % задавате скоростта по x
            %на ляво
            vecVelY(index) = .05;
        elseif cx == 0
            disp('stop')
            msg.Linear.Y = 0; % задавате скоростта по x
            %на ляво
            vecVelY(index) = 0;
        else
            vecVelY(index) = 0;
            msg.Linear.Y = 0; % задавате скоростта по x
        %в центъра си
        end
        
        vecArea(index) = area;
        if area < 20000
            msg.Linear.X = -0.05;
            vecVelX(index) = -.05;
        elseif area > 60000
            msg.Linear.X = 0.05;
            vecVelX(index) = .05;
        elseif area > 2000 && area < 6000
           msg.Linear.X = 0;
           vecVelX(index) = 0;
        else
            msg.Linear.X = 0;
            vecVelX(index) = 0;
        end    

    end
    
    receivemsg = receive(sub);
    if index == 1
       if  sub.LatestMessage.Pose.Pose.Position.Y > 0
           yinit = sub.LatestMessage.Pose.Pose.Position.Y;
       else
           yinit = sub.LatestMessage.Pose.Pose.Position.Y;
       end
       if  sub.LatestMessage.Pose.Pose.Position.X > 0
           xinit = sub.LatestMessage.Pose.Pose.Position.X;
       else
           xinit = sub.LatestMessage.Pose.Pose.Position.X;
       end
    end
    pos_y(index) = sub.LatestMessage.Pose.Pose.Position.Y - yinit;
    pos_x(index) = sub.LatestMessage.Pose.Pose.Position.X - xinit;
        
    send(pub,msg);
end






