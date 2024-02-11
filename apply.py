import os
import json
import argparse

from common.glslViewer import GlslViewer
from common.footage import Footage

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', '-i', help="Input folder. Example `/footage/000`", type=str, required=True)
    parser.add_argument('--shader', '-s', help="Shader folder. Example 'shaders/pcl_patch'", type=str, required=True)
    parser.add_argument('--output', help="folder name", type=str, default='')
    parser.add_argument('--width', '-w', help="width", default=None)
    parser.add_argument('--height', help="height", default=None)
    parser.add_argument('--pixel', '-p', help="Pixel density", default='2')
    parser.add_argument('--prime', help="Use NV Prime", default=False, action='store_true')
    parser.add_argument('--ncurses', help="Use ncurses interface", default=False, action='store_true')
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

    if not args.ncurses:
        cmd += " --noncurses "

    # Add metadata
    if "frames" in data:
        cmd += " -e u_total_frames," + str( int(data["frames"]) ) + " "

    if "duration" in data:
        cmd += " -e u_duration," + str(data["duration"]) + " "

    if "width" in data:
        cmd += " -e u_width," + str(data["width"]) + " "

    if "height" in data:
        cmd += " -e u_height," + str(data["height"]) + " "

    if "field_of_view" in data:
        cmd += " -e u_fov," + str(data["field_of_view"]) + " "

    if "focal_length" in data:
        cmd += " -e u_focal_length," + str(data["focal_length"]) + " "
    
    if "principal_point" in data:
        cmd += " -e u_principal_point," + str(data["principal_point"][0]) + "," + str(data["principal_point"][1]) + " "
    
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

    if args.prime:
        cmd = "prime-run " + cmd

    print(cmd) 
    os.system(cmd)

    

