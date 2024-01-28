#ifdef GL_ES
precision highp float;
#endif

uniform sampler2D   u_band_rgba;

uniform sampler2D   u_band_flow;
uniform vec2        u_band_flowResolution;
uniform float       u_band_flow_dist;

uniform vec2        u_resolution;
uniform float       u_time;

#include "lygia/space/ratio.glsl"
#include "lygia/sample/opticalFlow.glsl"

#define ARROWS_STYLE_LINE
#define ARROWS_TILE_SIZE 16.0

#include "lygia/draw/arrows.glsl"
#include "lygia/color/palette/heatmap.glsl"

void main() {
    vec4 color = vec4(0.0, 0.0, 0.0, 1.0);
    vec2 pixel = 1.0/u_resolution;
    vec2 st = gl_FragCoord.xy * pixel;
    vec2 uv = ratio(st, u_resolution);

    color = texture2D(u_band_rgba, st);

    vec2 dir = sampleOpticalFlow(u_band_flow, st, u_band_flowResolution, u_band_flow_dist);
    
    // color = vec4(vec3(depth), 1.);
    vec3 dir_color = heatmap( saturate(atan(dir.y, dir.x) / TAU + 0.5) );
    color.rgb += dir_color * arrows(st, dir, u_resolution) * smoothstep(0.0, 0.01, length(dir));

    gl_FragColor = color;
}
