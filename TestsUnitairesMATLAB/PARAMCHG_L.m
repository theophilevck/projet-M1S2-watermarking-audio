close all; clear all; clc;

addpath(genpath('01-Echo-Hiding-Single-Kernel'));
addpath(genpath('02-Echo-Hiding-NP-Kernel'));
addpath(genpath('03-Echo-Hiding-BF-Kernel'));
addpath(genpath('04-Echo-Hiding-Mirrored-Kernel'));
addpath(genpath('05-Echo-Hiding-Time-Spread'));

audio = audioload();

text = 'Message Echo-Cache Plus long pour favoriser la precision des erreurs fvdghefhzigifzf54g1ze5g5z1eg32z1fg535z41v3ezr4vg1er64vgf1egr6z41rvg36zer41vg6r7z4r*6g41z6g451zg-hzr4g6';

output = zeros(512, 1);
output2 = zeros(512, 1);
output3 = zeros(512, 1);
output4 = zeros(512, 1);
output5 = zeros(512, 1);

j = 0;
for i = 257:8:4096
    j = j + 1;
    out = echo_enc_single(audio.data, text, 128, 256, 0.5, i);
    out2 = echo_enc_np(audio.data, text, 128, 256, 0.5, i);
    out3 = echo_enc_bf(audio.data, text, 128, 256, 0.5, i);
    out4 = echo_enc_mirror(audio.data, text, 128, 256, 0.5, i);
    out5 = echo_enc_ts(audio.data, text, 128, 256, 0.04, i);

    msg = echo_dec(out, i, 128, 256);
    err = BER(text,msg);
    output(j) = err;
    
    msg = echo_dec(out2, i, 128, 256);
    err = BER(text,msg);
    output2(j) = err;
    
    msg = echo_dec(out3, i, 128, 256);
    err = BER(text,msg);
    output3(j) = err;
    
    msg = echo_dec(out4, i, 128, 256);
    err = BER(text,msg);
    output4(j) = err;
    
    msg = echo_dec_ts(out5, i, 128, 256);
    err = BER(text,msg);
    output5(j) = err;
end

figure;
hold on;
plot(256:8:4096, output(1:j+1));
plot(256:8:4096, output2(1:j+1));
plot(256:8:4096, output3(1:j+1));
plot(256:8:4096, output4(1:j+1));
plot(256:8:4096, output5(1:j+1));
xlabel('Segment Size: L');
ylabel('Percent of Decode Errors');
legend({'Echo Single', 'Echo Bipolar', 'Echo BF', 'Echo BF Bipolar', 'Echo Time-Spread'}, 'location', 'northeast');
