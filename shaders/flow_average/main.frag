#ifdef GL_ES
precision highp float;
#endif

uniform sampler2D   u_band_rgba;

uniform sampler2D   u_band_flow;
uniform vec2        u_band_flowResolution;
uniform float       u_band_flowCurrentFrame;
uniform float       u_band_flow_dist;

uniform sampler2D   u_pyramid0;
uniform sampler2D   u_pyramidTex0;
uniform sampler2D   u_pyramidTex1;
uniform int         u_pyramidDepth;
uniform int         u_pyramidTotalDepth;
uniform bool        u_pyramidUpscaling;

uniform sampler2D   u_doubleBuffer0; // 0.5

uniform vec2        u_resolution;
uniform float       u_time;
uniform float       u_total_frames;
uniform int         u_frame;

varying vec2        v_texcoord;

#define LEVEL 2
#define AVERAGE 0.5

#define ARROWS_STYLE_LINE
#define ARROWS_TILE_SIZE pow(2.0, float(LEVEL + 1))

#include "lygia/math/const.glsl"
#include "lygia/space/scale.glsl"
#include "lygia/color/palette/heatmap.glsl"
#include "lygia/draw/arrows.glsl"
#include "lygia/sample/opticalFlow.glsl"
#include "lygia/sample/nearest.glsl"
#include "lygia/sample/clamp2edge.glsl"
#include "lygia/morphological/pyramid/downscale.glsl"

vec3 colorizeAngle(vec2 _dir) {
    float angle = atan(_dir.y, _dir.x);
    float hue = (angle + PI) / TAU;
    return heatmap(hue);
}

void main() {
    vec4 color = vec4(0.0, 0.0, 0.0, 1.0);
    vec2 pixel = 1.0/u_resolution;
    vec2 st = v_texcoord;

    #if defined(PYRAMID_0)
    color = texture2D(u_band_flow, st);

    #elif defined(PYRAMID_ALGORITHM)
    if (!u_pyramidUpscaling) {
        color = pyramidDownscale(u_pyramidTex0, st, pixel);
        color.rgb /= color.a;
    }
    else {
        if (u_pyramidDepth > LEVEL)
            color = texture2D(u_pyramidTex0, st);
        else 
            color = texture2D(u_pyramidTex1, st);
    }
    color.a = 1.0;

    #elif defined(DOUBLE_BUFFER_0)

    color.xy = texture2D(u_doubleBuffer0, st).xy * (AVERAGE);
    vec2 dir = sampleOpticalFlow(u_pyramid0, st, u_band_flowResolution, u_band_flow_dist) * 2.0;
    color.xy += dir * (1.0-AVERAGE);

    #else

    color = texture2D(u_band_rgba, st);

    vec2 dir = sampleNearest(u_doubleBuffer0, st, u_resolution).xy;
    color.rgb += colorizeAngle(dir) * arrows(st, dir, u_resolution) * smoothstep(0.0, 0.005, length(dir));

    #endif

    gl_FragColor = color;
}
