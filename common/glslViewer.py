from os.path import join, abspath, exists
from copy import deepcopy

import yaml

class GlslViewer(object):
    def __init__( self, path: str, ):

        # folder containing the shaders and the manifest
        self.folder = path

        # Open an past the manifest
        self.manifest = yaml.load(open(join(self.folder, "manifest.yaml")).read(), Loader=yaml.FullLoader)

        # GlslViewer have different ways to load uniform values that uniform textures
        self.uniform_values: dict = {}
        self.uniform_textures: dict = {}

    def load_values_from(self, values: dict, pre: str = ""):
        for v in values:
            # if type is not specify try to guess it
            if not "type" in values[v]:
                if v in self.uniform_textures:
                    values[pre + v]["type"] = "sampler2D"
                elif v in self.uniform_values:
                    values[pre + v]["type"] = self.uniform_values[pre + v]["type"]
                else:
                    raise Exception(f"Cannot identify value {pre + v} type")

            if values[v]["type"] == "sampler2D":
                self.load_texture(pre + v, values[v]["value"])
                
            else:
                uniform: dict = deepcopy(values[v])
                self.uniform_values[pre + v] = uniform


    def load_texture(self, name: str, url: str):
        self.uniform_textures[name] = {}
        self.uniform_textures[name]["url"] = join(self.folder, url)


    def cmd(self, layer, pixel_density = 1.0):
        cmd = "glslViewer -l -Ishaders "
        cmd += join(self.folder, "main.frag") + " "
        if exists(abspath(join(self.folder, "main.vert"))):
            cmd += join(self.folder, "main.vert") + " " 
        if exists(abspath(join(self.folder, "geom.ply"))):
            cmd += join(self.folder, "geom.ply")  + " "
        elif exists(abspath(join(self.folder, "geom.glb"))):
            cmd += join(self.folder, "geom.glb")  + " "
        elif exists(abspath(join(self.folder, "geom.obj"))):
            cmd += join(self.folder, "geom.obj")  + " "
        cmd += " --fps " + str(layer.fps)


        width = layer.width/pixel_density
        height = layer.height/pixel_density

        if "scale" in self.manifest:
            if "width" in self.manifest["scale"]:
                width *= self.manifest["scale"]["width"]
            if "height" in self.manifest["scale"]:
                height *= self.manifest["scale"]["height"]

        cmd += " -w " + str(width) + " -h " + str(height)

        if "commands" in self.manifest:
            for e in self.manifest["commands"]:
                cmd += " -e " + e

        for b in layer.bands:
            if b in self.manifest["sources"]:

                if "url" in layer.bands[b]:
                    if b != "camera":
                        cmd += " --u_band_" + b

                    cmd +=  " " + layer.bands[b]["url"]

                if "values" in layer.bands[b]:
                    self.load_values_from( layer.bands[b]["values"], pre="u_band_" + b + "_" )

        if len(self.uniform_textures) > 0:
            cmd += " --vFlip"
            for t in self.uniform_textures:
                cmd += " --" + t + " " + self.uniform_textures[t]["url"]

        for u in self.uniform_values:
            if "value" in self.uniform_values[u]:
                if self.uniform_values[u]["type"] == "bool":
                    uniform = self.uniform_values[u]["value"]
                    if uniform:
                        cmd += " -e " + u + ",1"
                    else:
                        cmd += " -e " + u + ",0"

                elif self.uniform_values[u]["type"] != "sampler2D":
                    uniform = self.uniform_values[u]["value"]
                    if type(uniform) is list:
                        cmd += " -e " + u + "," + ",".join( [str(v) for v in uniform] )
                    else:
                        cmd += " -e " + u + "," + str(uniform)
            elif "url" in self.uniform_values[u]:
                cmd += " --" + u + " " + join(layer.folder, self.uniform_values[u]["url"])

        return cmd


