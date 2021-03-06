#!/usr/bin/env python
# coding=UTF-8


import rospy
import rosbag
import argparse
import tf2_msgs.msg
import geometry_msgs.msg


def add_tf(inbag_filename, outbag_filename, source_frame, target_frame, position, rotation, time_increment):
    print ' Processing input bagfile: %s' % (inbag_filename)
    print '               Adding tfs: [%s -> %s]' % (source_frame, target_frame)
    print '                 Position: [x: %f, y: %f, z: %f]' % (position[0], position[1], position[2])
    print '                 Rotation: [x: %f, y: %f, z: %f, w: %f]' % (rotation[0], rotation[1], rotation[2], rotation[3])

    transform_msg = tf2_msgs.msg.TFMessage()
    transform_msg.transforms.append(geometry_msgs.msg.TransformStamped())
    transform_msg.transforms[0].header.frame_id = source_frame
    transform_msg.transforms[0].header.seq = 0
    transform_msg.transforms[0].child_frame_id = target_frame
    transform_msg.transforms[0].transform.translation.x = position[0]
    transform_msg.transforms[0].transform.translation.y = position[1]
    transform_msg.transforms[0].transform.translation.z = position[2]
    transform_msg.transforms[0].transform.rotation.x = rotation[0]
    transform_msg.transforms[0].transform.rotation.y = rotation[1]
    transform_msg.transforms[0].transform.rotation.z = rotation[2]
    transform_msg.transforms[0].transform.rotation.w = rotation[3]

    inbag = rosbag.Bag(inbag_filename,'r')
    outbag = rosbag.Bag(outbag_filename, 'w', rosbag.bag.Compression.BZ2)
    time = rospy.Time(inbag.get_start_time())
    end_time = rospy.Time(inbag.get_end_time())
    transform_msg.transforms[0].header.stamp = time
    time_increment_duration = rospy.Duration(time_increment)

    print '            Time interval: [%f] -> [%f]' % (time.to_sec(), end_time.to_sec())

    number_messages_added = 0
    for topic, msg, t in inbag.read_messages():
        while time.to_sec() < t.to_sec():
            outbag.write("/tf", transform_msg, time)
            time += time_increment_duration
            transform_msg.transforms[0].header.stamp = time
            transform_msg.transforms[0].header.seq += 1
            number_messages_added += 1
        outbag.write(topic, msg, t)
    
    while time.to_sec() < end_time.to_sec():
        outbag.write("/tf", transform_msg, time)
        time += time_increment_duration
        transform_msg.transforms[0].header.stamp = time
        transform_msg.transforms[0].header.seq += 1
        number_messages_added += 1

    print 'Added %i TF messages' % (number_messages_added)
    print 'Closing output bagfile %s' % (outbag_filename)
    inbag.close()
    outbag.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Script to add tfs to rosbags')
    parser.add_argument('-i', metavar='BAGFILE_FILENAME', required=True, help='Input bagfile')
    parser.add_argument('-o', metavar='OUTPUT_BAGFILE', required=True, help='Output bagfile')
    parser.add_argument('-s', metavar='SOURCE_FRAME_ID', required=True, help='Header frame_id')
    parser.add_argument('-t', metavar='TARGET_FRAME_ID', required=True, help='Child frame_id')
    parser.add_argument('-r', type=float, required=False, default=0.02, help='Time increment between TF messages')
    parser.add_argument('-X', type=float, required=False, default=0.0, help='x position')
    parser.add_argument('-Y', type=float, required=False, default=0.0, help='y position')
    parser.add_argument('-Z', type=float, required=False, default=0.0, help='z position')
    parser.add_argument('-x', type=float, required=False, default=0.0, help='x rotation')
    parser.add_argument('-y', type=float, required=False, default=0.0, help='y rotation')
    parser.add_argument('-z', type=float, required=False, default=0.0, help='z rotation')
    parser.add_argument('-w', type=float, required=False, default=1.0, help='w rotation')
    args = parser.parse_args()

    try:
      add_tf(args.i, args.o, args.s, args.t, [args.X, args.Y, args.Z], [args.x, args.y, args.z, args.w], args.r)
      exit(0)
    except Exception, e:
      import traceback
      traceback.print_exc()
