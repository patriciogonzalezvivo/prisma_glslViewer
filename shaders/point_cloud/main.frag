#version 120 

#ifdef GL_ES
precision highp float;
#endif


uniform sampler2D   u_doubleBuffer0;

uniform sampler2D   u_band_rgba;
uniform vec2        u_band_rgbaResolution;

uniform sampler2D   u_band_depth;
uniform vec2        u_band_depthResolution;
uniform float       u_band_depth_min;
uniform float       u_band_depth_max;

uniform vec2        u_resolution;
uniform float       u_time;
uniform int         u_frame;

varying vec4        v_color;
varying vec2        v_texcoord;

#include "lygia/math/const.glsl"
#include "lygia/math/saturate.glsl"
#include "lygia/math/decimate.glsl"
#include "lygia/color/luma.glsl"

#include "lygia/sample/clamp2edge.glsl"
#define SAMPLEHEATMAP_SAMPLE_FNC(TEX, UV) sampleClamp2edge(TEX, UV).rgb
#include "lygia/sample/heatmap.glsl"

#define EDGE_SAMPLER_FNC(TEX, UV) sampleHeatmap(TEX, UV)
#include "lygia/filter/edge.glsl"

#include "lygia/lighting/ray/direction.glsl"
#include "lygia/lighting/ray/cast.glsl"

void main() {
    vec4 color = vec4(0.0, 0.0, 0.0, 1.0);
    vec2 pixel = 1.0 / u_resolution;
    vec2 st = gl_FragCoord.xy * pixel;
    vec2 uv = v_texcoord;

#if defined(DOUBLE_BUFFER_0)
    Ray ray = rayDirection(vec3(0.0, 0.0, 3.0), uv * 2.0 - 1.0, u_band_rgbaResolution, 45.);
    float depth = sampleHeatmap(u_band_depth, uv, u_band_depth_min, u_band_depth_max);
    color.xyz = rayCast(ray, depth);

    vec2 depth_pixel = 1.0/u_band_depthResolution;
    color.a = 1.0-edge(u_band_depth, uv, depth_pixel * 5.0);

    vec4 prevColor = texture2D(u_doubleBuffer0, uv);
    color = mix(prevColor, color, 0.25);

#else
    color = v_color;

#endif

    gl_FragColor = color;
}
