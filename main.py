import droplet

import jinja2
import math
import os
import subprocess
import webapp2

from paste import httpserver
from paste.cascade import Cascade
from paste.urlparser import StaticURLParser


HOST = '127.0.0.1'
PORT = '8080'

pwd = os.path.dirname(__file__)

class MainPage(webapp2.RequestHandler):
    def get(self):
        template_loader = jinja2.FileSystemLoader(searchpath=pwd)
        template_env = jinja2.Environment(loader=template_loader)
        template = template_env.get_template('index.html')
        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write(template.render())


class GenerateFramesPage(webapp2.RequestHandler):
    def get(self):
        frame_path_prefix = '/Users/Sean/Documents/Programs/Projects/DropletMeasurement/resources/'
        video_file = self.request.get('video_file')
        seconds_per_frame = self.request.get('seconds_per_frame')
        video_basename = os.path.basename(video_file)
        file_type_index = video_file.rfind('.')
        video_basename = video_file[:file_type_index]
        frame_dir = os.path.join(frame_path_prefix, video_basename, 'raw')
        frame_path = os.path.join(frame_dir, 'frame%04d.png')
        if not os.path.exists(frame_dir):
            os.makedirs(frame_dir)
        else:
            # TODO: Handle this correctly. Maybe don't exit early.
            self.response.out.write(frame_path)
            return
        exit_code = 0
        self.response.headers['Content-Type'] = 'text/plain'
        try:
            exit_code = subprocess.check_call([
                'ffmpeg',
                '-i', video_file,
                '-r', '1/%s' % seconds_per_frame,
                frame_path])
            self.response.out.write(frame_path)
        except subprocess.CalledProcessError as err:
            self.response.out.write('Error: %s' % err)


class FindCirclesPage(webapp2.RequestHandler):
    def get(self):
        frame_path = self.request.get('frame_path')
        for file in sorted(os.listdir(os.path.dirname(frame_path))):
            droplet.find_circles_in_image(os.path.dirname(frame_path), file)
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('success')


def write_csv(time_offset, times, radii):
    contents = 'ID,Time Stamp,Adjusted Time,Droplet 1 Radius,Droplet 1 Volume,Droplet 2 Radius,Droplet 2 Volume,Total Volume,DIB Radius,Contact Angle,Radial Distance\n'
    for time, radius in zip(times, radii):
        #ID ####,time,adjusted_time,r1,v1,r2,v2,total v, #### DIB Radius,Contact Angle,Radial Distance
        adjusted_time = time - time_offset
        r1 = radius[0]
        v1 = 4.0 / 3 * math.pi * (r1 ** 3)
        r2 = radius[1]
        v2 = 4.0 / 3 * math.pi * (r2 ** 3)
        total_v = v1 + v2
        contents += '%f,%f,%f,%f,%f,%f,%f\n' % (time, adjusted_time, r1, v1, r2, v2, total_v)


def main():
    web_app = webapp2.WSGIApplication([
        ('/', MainPage),
        ('/generate-frames', GenerateFramesPage),
        ('/find-circles', FindCirclesPage),
    ], debug=True)
    resources_app = StaticURLParser('resources/')
    app = Cascade([resources_app, web_app])
    httpserver.serve(app, host=HOST, port=PORT)

if __name__ == '__main__':
    main()
