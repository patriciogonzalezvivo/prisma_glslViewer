#ifdef GL_ES
precision highp float;
#endif

uniform sampler2D   u_band_rgba;
uniform vec2        u_band_rgbaResolution;

uniform sampler2D   u_doubleBuffer0;

uniform mat4        u_modelMatrix;
uniform mat4        u_viewMatrix;
uniform mat4        u_projectionMatrix;
uniform mat4        u_modelViewProjectionMatrix;

uniform vec3        u_camera;
uniform float       u_cameraDistance;

uniform vec2        u_resolution;
uniform float       u_time;

attribute vec4      a_position;
varying vec4        v_position;

varying vec4        v_color;
varying vec2        v_texcoord;

#include "lygia/math/saturate.glsl"
#include "lygia/sample/nearest.glsl"

void main(void) {
    v_position = a_position;
    v_texcoord = a_position.xy;

    vec2 uv = v_texcoord;

    v_color = sampleNearest(u_band_rgba, uv, u_resolution);
    vec4 data = sampleNearest(u_doubleBuffer0, uv, u_resolution);

    v_position.xyz = data.xyz;
    gl_PointSize = 3.0;
    gl_PointSize *= data.w;
    
    gl_Position = u_projectionMatrix * u_viewMatrix * v_position;
}
