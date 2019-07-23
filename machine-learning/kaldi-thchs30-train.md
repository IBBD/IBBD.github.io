# 基于Kaldi，训练中文语音识别模型

- kaldi官网：https://github.com/kaldi-asr/kaldi/
- 参考链接：http://pelhans.com/tags/#Kaldi

## x01: 下载thchs30语料库

THCHS30是一个经典的中文语音数据集，包含了1万余条语音文件，大约40小时的中文语音数据，内容以文章诗句为主，全部为女声。它是由清华大学语音与语言技术中心（CSLT）出版的开放式中文语音数据库。原创录音于2002年由朱晓燕教授在清华大学计算机科学系智能与系统重点实验室监督下进行，原名为“TCMSD”，代表“清华连续”普通话语音数据库’。13年后的出版由王东博士发起，并得到了朱晓燕教授的支持。他们希望为语音识别领域的新入门的研究人员提供玩具级别的数据库，因此，数据库对学术用户完全免费。

虽然是玩具级，可其需要下载的文件可不小，需要有相当耐心：

```sh
wget http://www.openslr.org/resources/18/data_thchs30.tgz
wget http://www.openslr.org/resources/18/test-noise.tgz
wget http://www.openslr.org/resources/18/resource.tgz
```

解压并保存到某文件夹。

## x02 下载kaldi镜像

```sh
# 对应dockerfile：https://github.com/kaldi-asr/kaldi/blob/master/docker/ubuntu16.04-gpu/Dockerfile
docker pull kaldiasr/kaldi:gpu-latest
```

如果没有GPU，则直接下载cpu版本。

## x03 docker启动脚本
在语料库根目录下，运行以下脚本：

```sh
sudo docker run -ti --name=kaldi \
    -v "$PWD":/thchs30 \
    --runtime=nvidia \
    -w /kaldi \
    kaldiasr/kaldi:gpu-latest \
    /bin/bash
```

默认进入目录`/opt/kaldi`。

## x04 修改训练脚本
到这个步骤需要修改容器内部的训练脚本，最好在外部修改好之后，再复制到容器里面。

```sh
cd egs/thchs30/s5/

# 修改cmd.sh
#export train_cmd=queue.pl
#export decode_cmd="queue.pl --mem 4G"
#export mkgraph_cmd="queue.pl --mem 8G"
#export cuda_cmd="queue.pl --gpu 1"
export train_cmd=run.pl
export decode_cmd="run.pl --mem 4G"
export mkgraph_cmd="run.pl --mem 8G"
export cuda_cmd="run.pl --gpu 1"

# 修改run.sh
#n=4      #parallel jobs
n=8      #parallel jobs

#thchs=/nfs/public/materials/data/thchs30-openslr
thchs=/thchs30
```

本地使用的是2080Ti的显卡。

## x05 运行

```sh
./run.sh
```

大概有几个过程：数据准备，monophone单音素训练， tri1三因素训练， trib2进行lda_mllt特征变换，trib3进行sat自然语言适应，trib4做quick，训练DNN模型，训练DAE模型（DAE:深度自动编码器，用于去噪）

然后就是等。。。

运行过程中，可能会有如下的提示信息，不过不影响：

steps/make_fbank.sh: [info]: no segments file exists: assuming wav.scp indexed by utterance.

训练loss的下降过程：

```
CROSSVAL PRERUN AVG.LOSS 8.3997 (Xent),
ITERATION 01: TRAIN AVG.LOSS 2.1030, (lrate0.008), CROSSVAL AVG.LOSS 2.2399, nnet accepted (nnet_iter01_learnrate0.008_tr2.1030_cv2.2399)
ITERATION 02: TRAIN AVG.LOSS 1.4187, (lrate0.008), CROSSVAL AVG.LOSS 2.0468, nnet accepted (nnet_iter02_learnrate0.008_tr1.4187_cv2.0468)
ITERATION 03: TRAIN AVG.LOSS 1.2506, (lrate0.008), CROSSVAL AVG.LOSS 1.9796, nnet accepted (nnet_iter03_learnrate0.008_tr1.2506_cv1.9796)
ITERATION 04: TRAIN AVG.LOSS 1.1478, (lrate0.008), CROSSVAL AVG.LOSS 1.9544, nnet accepted (nnet_iter04_learnrate0.008_tr1.1478_cv1.9544)
ITERATION 05: TRAIN AVG.LOSS 1.0731, (lrate0.008), CROSSVAL AVG.LOSS 1.9514, nnet accepted (nnet_iter05_learnrate0.008_tr1.0731_cv1.9514)
ITERATION 06: TRAIN AVG.LOSS 1.0114, (lrate0.004), CROSSVAL AVG.LOSS 1.7779, nnet accepted (nnet_iter06_learnrate0.004_tr1.0114_cv1.7779)
ITERATION 07: TRAIN AVG.LOSS 0.9895, (lrate0.002), CROSSVAL AVG.LOSS 1.6401, nnet accepted (nnet_iter07_learnrate0.002_tr0.9895_cv1.6401)
ITERATION 08: TRAIN AVG.LOSS 0.9935, (lrate0.001), CROSSVAL AVG.LOSS 1.5487, nnet accepted (nnet_iter08_learnrate0.001_tr0.9935_cv1.5487)
ITERATION 09: TRAIN AVG.LOSS 1.0035, (lrate0.0005), CROSSVAL AVG.LOSS 1.4917, nnet accepted (nnet_iter09_learnrate0.0005_tr1.0035_cv1.4917)
ITERATION 10: TRAIN AVG.LOSS 1.0112, (lrate0.00025), CROSSVAL AVG.LOSS 1.4567, nnet accepted (nnet_iter10_learnrate0.00025_tr1.0112_cv1.4567)
ITERATION 11: TRAIN AVG.LOSS 1.0153, (lrate0.000125), CROSSVAL AVG.LOSS 1.4360, nnet accepted (nnet_iter11_learnrate0.000125_tr1.0153_cv1.4360)
ITERATION 12: TRAIN AVG.LOSS 1.0168, (lrate6.25e-05), CROSSVAL AVG.LOSS 1.4244, nnet accepted (nnet_iter12_learnrate6.25e-05_tr1.0168_cv1.4244)
ITERATION 13: TRAIN AVG.LOSS 1.0168, (lrate3.125e-05), CROSSVAL AVG.LOSS 1.4183, nnet accepted (nnet_iter13_learnrate3.125e-05_tr1.0168_cv1.4183)
ITERATION 14: TRAIN AVG.LOSS 1.0163, (lrate1.5625e-05), CROSSVAL AVG.LOSS 1.4154, nnet accepted (nnet_iter14_learnrate1.5625e-05_tr1.0163_cv1.4154)
ITERATION 15: TRAIN AVG.LOSS 1.0157, (lrate7.8125e-06), CROSSVAL AVG.LOSS 1.4139, nnet accepted (nnet_iter15_learnrate7.8125e-06_tr1.0157_cv1.4139)
ITERATION 16: TRAIN AVG.LOSS 1.0153, (lrate3.90625e-06), CROSSVAL AVG.LOSS 1.4133, nnet accepted (nnet_iter16_learnrate3.90625e-06_tr1.0153_cv1.4133)
finished, too small rel. improvement 0.000466784
```

在进行DNN训练的时候，显存占用大概6G。







