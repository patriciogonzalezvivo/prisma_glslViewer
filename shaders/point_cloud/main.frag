#version 120 

#ifdef GL_ES
precision highp float;
#endif

uniform sampler2D   u_band_rgba;
uniform vec2        u_band_rgbaResolution;

uniform sampler2D   u_band_depth_patchfusion;
uniform vec2        u_band_depth_patchfusionResolution;
uniform float       u_band_depth_patchfusion_min;
uniform float       u_band_depth_patchfusion_max;

uniform sampler2D   u_doubleBuffer0;

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
#include "lygia/draw/stroke.glsl"

void main() {
    vec4 color = vec4(0.0, 0.0, 0.0, 1.0);
    vec2 pixel = 1.0 / u_resolution;
    vec2 st = gl_FragCoord.xy * pixel;
    vec2 uv = v_texcoord;

    vec2 grid = vec2(4.0);
    float totalCells = grid.x * grid.y;
    float time = fract(u_time * 0.1) * totalCells;

    vec2 uv1 = uv * grid;
    vec2 uv1_i = floor(uv1);  // integer
    vec2 uv1_f = fract(uv1);
    
    // 100%
    vec2 head = vec2(floor(mod(time,grid.x)), grid.y-floor(time/grid.x)-1.0 );

    // Reveil
    float pct = step(head.y, uv1_i.y-1.0) + step(uv1_i.x, head.x) * step(head.y, uv1_i.y);
    pct = saturate(pct);

#if defined(DOUBLE_BUFFER_0)
    Ray ray = rayDirection(vec3(0.0, 0.0, 3.0), uv * 2.0 - 1.0, u_band_rgbaResolution, 45.0);
    float depth = sampleHeatmap(u_band_depth_patchfusion, uv, u_band_depth_patchfusion_min, u_band_depth_patchfusion_max);
    color.xyz = rayCast(ray, depth);

    vec2 depth_pixel = 1.0/u_band_depth_patchfusionResolution;
    color.a = 1.0-edge(u_band_depth_patchfusion, uv, depth_pixel * 5.0);

    vec4 empty = vec4(rayCast(ray, u_band_depth_patchfusion_max * 0.5), 1.0);


    color = mix(empty, color, pct);

    vec4 prevColor = texture2D(u_doubleBuffer0, uv);
    color = mix(prevColor, color, 0.25);

#else
    color = v_color;
    
    vec2 w = pixel * 2.0;
    color.rgb += (stroke(uv1_f.x, 0.0, w.x, 0.001) + stroke(uv1_f.y, 0.0, w.y, 0.001)) * stroke(pct, 0.1, 1.0);

    if (head == uv1_i) {
        color.rgb = texture2D(u_band_depth_patchfusion, uv).rgb * (0.5 + luma(v_color.rgb));

    }

#endif

    gl_FragColor = color;
}
