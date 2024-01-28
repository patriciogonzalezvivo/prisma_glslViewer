import os
import json
import argparse

from common.glslViewer import GlslViewer
from common.footage import Footage

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', '-i', help="Input folder. Ex: `/footage/000`", type=str, required=True)
    parser.add_argument('--shader', '-s', help="Shader folder. Ex: 'shaders/pcl_patch'", type=str, required=True)
    parser.add_argument('--output', help="folder name", type=str, default='')
    parser.add_argument('--width', '-w', help="width", default=None)
    parser.add_argument('--height', help="height", default=None)
    parser.add_argument('--pixel', '-p', help="Pixel density", default='2')
    parser.add_argument('--prime', help="Use NV Prime", default=False, action='store_true')
    args = parser.parse_args()

    input_path = args.input
    input_metadata = args.input + "/metadata.json"
    
    data = None
    fps = 24
    frames = fps * 3
    if os.path.isfile(input_metadata):
        data = json.load( open(input_metadata) )

    if data:
        if "fps" in data:
            fps = data["fps"]

        if "frames" in data:
            frames = int(data["frames"]) 

    # Fake layer/frame to be process by all fitlers
    footage = Footage(args.input, metadata=data)
    
    # create a filter
    shader = GlslViewer(path=args.shader)

    if args.width:
        footage.setWidth( int(args.width) )
    
    if args.height:
        footage.setHeight( int(args.height) )

    pixel_density = float(args.pixel)
    if len(args.output) > 0:
        pixel_density = 1.0

    cmd = shader.cmd(footage, pixel_density)
    cmd += " --noncurses "

    if "frames" in data:
        frames = int(data["frames"]) 
        cmd += " -e u_total_frames," + str(frames) + " "
    
    if len(args.output) > 0:
        cmd += ' --noncurses --headless '
                
        output_filename = os.path.basename(args.output)
        output_basename = output_filename.rsplit( ".", 1 )[ 0 ]
        output_extension = output_filename.rsplit( ".", 1 )[ 1 ]
        output_video = output_extension == "mp4"

        if output_video:
            cmd += ' -E frames,0,' + str( frames )
            print(cmd)
            os.system(cmd)

            cmd = "ffmpeg -r " + str( fps ) + " -i %05d.png -vcodec libx264 -crf 25 -pix_fmt yuv420p tmp.mp4"
            os.system(cmd)

            cmd = "mv tmp.mp4 " + args.output
            os.system(cmd)

            cmd = "rm ?????.png"

        else:
            cmd += ' -E screenshot,' + args.output

    # for i in range(3, len(sys.argv)):
    #     if sys.argv[i].isdigit():
    #         cmd += ' -p ' + sys.argv[i]
    #     elif sys.argv[i][0] == '-':
    #         cmd += ' ' + sys.argv[i]
    #     else:
    #         cmd += ' -e ' + sys.argv[i]
    # cmd += " --noncurses "

    if args.prime:
        cmd = "prime-run " + cmd

    print(cmd) 
    os.system(cmd)

    

