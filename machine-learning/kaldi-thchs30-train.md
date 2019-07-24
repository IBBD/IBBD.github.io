# 基于Kaldi，训练中文语音识别模型

- kaldi官网：https://github.com/kaldi-asr/kaldi/
- 参考链接：http://pelhans.com/tags/#Kaldi
- 脚本说明：https://blog.csdn.net/KanShiMeKan/article/details/71250135

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
    -v "$PWD":/nfs/public/materials/data/thchs30-openslr \
    --runtime=nvidia \
    -w /opt/kaldi/egs/thchs30/s5 \
    kaldiasr/kaldi:gpu-latest \
    /bin/bash
```

说明：开始时使用“gpu-latest”这个镜像，训练完成之后没有找到相应的模型，血的教训呀。

使用“gpu-5.4”这个版本的镜像在训练dnn模型时会报错：

```
### Before posting the error to forum, please try following:
### 1) update kaldi & cuda-toolkit (& GPU driver),
### 2) re-run 'src/configure',
### 3) re-compile kaldi by 'make clean; make -j depend; make -j'
###
### If the problem persists, please send us your:
### - GPU model name, cuda-toolkit version, driver version (run nvidia-smi), variable $(CUDA_ARCH) from src/kaldi.mk
run.pl: job failed, log is in exp/tri4b_dnn/log/train_nnet.log
```

应该是cuda的版本问题。

## x04 修改训练脚本
到这个步骤需要修改容器内部的训练脚本，最好在外部修改好之后，再复制到容器里面。

```sh
cd egs/thchs30/s5/

# 修改cmd.sh
#export train_cmd=queue.pl
#export decode_cmd="queue.pl --mem 4G"
#export mkgraph_cmd="queue.pl --mem 8G"
#export cuda_cmd="queue.pl --gpu 1"
# 下面这组配置需要超过15G的空余内存，会导致错误发生
export train_cmd="run.pl --max-jobs-run 8"
export decode_cmd="run.pl --max-jobs-run 8"
export mkgraph_cmd="run.pl --max-jobs-run 8"
export cuda_cmd="run.pl --max-jobs-run 2"

# 下面这组配置高峰时也会超过15G内存，还是会报很多错误
export train_cmd="run.pl --max-jobs-run 6"
export decode_cmd="run.pl --max-jobs-run 6"
export mkgraph_cmd="run.pl --max-jobs-run 6"
export cuda_cmd="run.pl --max-jobs-run 2"

# 能运行到dnn，不过还是会报错
export train_cmd="run.pl --max-jobs-run 4"
export decode_cmd="run.pl --max-jobs-run 4"
export mkgraph_cmd="run.pl --max-jobs-run 4"
export cuda_cmd="run.pl --max-jobs-run 2"

# 这组配置
export train_cmd=run.pl
export decode_cmd="run.pl --mem 4G"
export mkgraph_cmd="run.pl --mem 8G"
export cuda_cmd="run.pl --gpu 2"

# 修改run.sh
#n=4      #parallel jobs
n=8       #parallel jobs

# docker已经映射到这个目录
thchs=/nfs/public/materials/data/thchs30-openslr
```

本地使用的是2080Ti的显卡。

## x05 运行

```sh
./run.sh
```

大概有几个过程：

- 数据准备
- 单音素模型训练(steps/train_mono.sh)(monophone model)：对应 exp 文件夹下产生一个 mono 的目录，里面以 .mdl 结尾的就保存了模型的参数。
- tri1三因素训练
- trib2进行lda_mllt特征变换
- trib3说话人自适应训练（SAT)
- 特征空间最大似然线性回归(Feature-space Maximum Likelihood Linear Regression, FMLLR)
- trib4做quick
- 训练DNN-HMM模型
- 训练DAE模型（DAE:深度自动编码器，用于去噪）: 通过对语音数据添加噪声来得到有噪音的数据，然后进行DNN训练

可以参考这个文章：http://www.huanglu.club/2017/02/17/kaldi-running-scripts.html

然后就是等。。。

运行过程中，可能会有如下的提示信息，警告信息和报错信息，不过不影响继续训练：

```sh
steps/make_mfcc.sh: [info]: no segments file exists: assuming wav.scp indexed by utterance.
WARNING (gmm-init-model[5.4.271~1-e50bd]:InitAmGmm():gmm-init-model.cc:55) Tree has pdf-id 208 with no stats; corresponding phone list: 209
steps/make_fbank.sh: [info]: no segments file exists: assuming wav.scp indexed by utterance.

# 网上提供的解决方法：https://blog.csdn.net/sut_wj/article/details/71993176
# 但是并不能解决
ERROR: FstHeader::Read: Bad FST header: -
ERROR (fstminimizeencoded[5.4.271~1-e50bd]:ReadFstKaldi():kaldi-fst-io.cc:35) Reading FST: error reading FST header from standard input

[ Stack-Trace: ]
kaldi::MessageLogger::HandleMessage(kaldi::LogMessageEnvelope const&, char const*)
kaldi::MessageLogger::~MessageLogger()
kaldi::FatalMessageLogger::~FatalMessageLogger()
fst::ReadFstKaldi(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >)
main
__libc_start_main
_start

# 下面这个应该是内存不足导致
Estimating fMLLR transforms
steps/decode.sh --cmd run.pl --mem 4G --nj 10 exp/tri1/graph_word data/mfcc/test exp/tri1/decode_test_word
decode.sh: feature type is delta
bash: line 1: 56995 Killed                  ( gmm-latgen-faster --max-active=7000 --beam=13.0 --lattice-beam=6.0 --acoustic-scale=0.083333 --allow-partial=true --word-symbol-table=exp/tri1/graph_word/words.txt exp/tri1/final.mdl exp/tri1/graph_word/HCLG.fst "ark,s,cs:apply-cmvn  --utt2spk=ark:data/mfcc/test/split10/6/utt2spk scp:data/mfcc/test/split10/6/cmvn.scp scp:data/mfcc/test/split10/6/feats.scp ark:- | add-deltas  ark:- ark:- |" "ark:|gzip -c > exp/tri1/decode_test_word/lat.6.gz" ) 2>> exp/tri1/decode_test_word/log/decode.6.log >> exp/tri1/decode_test_word/log/decode.6.log
```

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

在进行DNN训练的时候，显存占用大概6G。运行到这里大概2个半小时，后面就卡在下面这里了：

```
local/score.sh --cmd run.pl --mem 4G data/mfcc/test_phone exp/mono/graph_phone exp/mono/decode_test_phone
local/score.sh: scoring with word insertion penalty=0.0,0.5,1.0
```

卡在这里一动不动。。。

**当内存不足的时候，就容易报各种错误！**这时需要将并发数量减少，否则后面的训练可能会有各种问题。

跑到“steps/train_sat.sh”这个脚本的时候，内存暴涨，超出2G以上。

内存占用超出的时候，就会报错：

```
utils/mkgraph.sh: line 133: 46398 Done                    fsttablecompose $dir/Ha.fst "$clg"
     46399                       | fstdeterminizestar --use-log=true
     46400                       | fstrmsymbols $dir/disambig_tid.int
     46401                       | fstrmepslocal
     46402 Killed                  | fstminimizeencoded > $dir/HCLGa.fst.$$
```

## x06 查看结果文件

结果文件保存在当前目录的“RESULTS”文件中，如下：

```sh
#!/bin/bash
for x in exp/{mono,tri1,tri2b,tri3b,tri4b,tri4b_dnn,tri4b_dnn_mpe}/decode_test_phone* ; do [ -d $x ] && grep WER $x/wer_* | utils/best_wer.sh; done
#clean mono,tri1,tri2b,tri3b,GMM,DNN model
#clean test data
#phone task
%WER 34.00 [ 123105 / 362027, 17267 ins, 28402 del, 77436 sub ] exp/mono/decode_test_phone/wer_9_0.0
%WER 21.68 [ 78478 / 362027, 11305 ins, 16394 del, 50779 sub ] exp/tri1/decode_test_phone/wer_9_0.5
%WER 18.32 [ 66320 / 362027, 8860 ins, 14855 del, 42605 sub ] exp/tri2b/decode_test_phone/wer_9_0.5
%WER 15.98 [ 57853 / 362027, 8186 ins, 12404 del, 37263 sub ] exp/tri3b/decode_test_phone/wer_9_0.5
%WER 19.67 [ 71215 / 362027, 10156 ins, 15669 del, 45390 sub ] exp/tri3b/decode_test_phone.si/wer_9_0.5
%WER 14.28 [ 51699 / 362027, 7307 ins, 10875 del, 33517 sub ] exp/tri4b/decode_test_phone/wer_9_1.0
%WER 17.54 [ 63483 / 362027, 9898 ins, 12935 del, 40650 sub ] exp/tri4b/decode_test_phone.si/wer_9_0.5
%WER 10.38 [ 37582 / 362027, 8577 ins, 7008 del, 21997 sub ] exp/tri4b_dnn/decode_test_phone/wer_4_1.0
%WER 10.22 [ 36997 / 362027, 8497 ins, 6834 del, 21666 sub ] exp/tri4b_dnn_mpe/decode_test_phone_it1/wer_4_1.0
%WER 10.15 [ 36749 / 362027, 8435 ins, 6778 del, 21536 sub ] exp/tri4b_dnn_mpe/decode_test_phone_it2/wer_4_1.0
%WER 10.13 [ 36681 / 362027, 8427 ins, 6759 del, 21495 sub ] exp/tri4b_dnn_mpe/decode_test_phone_it3/wer_4_1.0

exit 0

for x in exp/{mono,tri1,tri2b,tri3b,tri4b,tri4b_dnn,tri4b_dnn_mpe}/decode_test_word* ; do [ -d $x ] && grep WER $x/wer_* | utils/best_wer.sh; done
#clean mono,tri1,tri2b,tri3b,GMM,DNN model
#clean test data
#word task
%WER 50.88 [ 41280 / 81139, 506 ins, 2393 del, 38381 sub ] exp/mono/decode_test_word/wer_9_0.0
%WER 35.97 [ 29188 / 81139, 531 ins, 1041 del, 27616 sub ] exp/tri1/decode_test_word/wer_10_0.0
%WER 32.14 [ 26078 / 81139, 418 ins, 1057 del, 24603 sub ] exp/tri2b/decode_test_word/wer_10_0.0
%WER 29.47 [ 23913 / 81139, 396 ins, 864 del, 22653 sub ] exp/tri3b/decode_test_word/wer_10_0.0
%WER 33.65 [ 27300 / 81139, 483 ins, 1049 del, 25768 sub ] exp/tri3b/decode_test_word.si/wer_9_0.0
%WER 28.07 [ 22776 / 81139, 418 ins, 762 del, 21596 sub ] exp/tri4b/decode_test_word/wer_11_0.0
%WER 31.50 [ 25559 / 81139, 511 ins, 928 del, 24120 sub ] exp/tri4b/decode_test_word.si/wer_10_0.0
%WER 23.68 [ 19217 / 81139, 490 ins, 597 del, 18130 sub ] exp/tri4b_dnn/decode_test_word/wer_7_0.0
%WER 23.44 [ 19022 / 81139, 465 ins, 576 del, 17981 sub ] exp/tri4b_dnn_mpe/decode_test_word_it1/wer_7_0.0
%WER 23.35 [ 18947 / 81139, 408 ins, 631 del, 17908 sub ] exp/tri4b_dnn_mpe/decode_test_word_it2/wer_8_0.0
%WER 23.30 [ 18904 / 81139, 406 ins, 622 del, 17876 sub ] exp/tri4b_dnn_mpe/decode_test_word_it3/wer_8_0.0

exit 0

for x in exp/{tri4b_dnn_mpe,tri4b_dnn_dae}/decode_phone_0db/{white,car,cafe}; do [ -d $x ] && grep WER $x/wer_* | utils/best_wer.sh; done
#clean MPE model and mixture DAE model
#0db noise test data
#phone task
%WER 89.56 [ 324225 / 362027, 285 ins, 308951 del, 14989 sub ] exp/tri4b_dnn_mpe/decode_phone_0db/white/wer_4_0.0
%WER 13.30 [ 48153 / 362027, 10504 ins, 8015 del, 29634 sub ] exp/tri4b_dnn_mpe/decode_phone_0db/car/wer_4_1.0
%WER 76.73 [ 277777 / 362027, 4072 ins, 247019 del, 26686 sub ] exp/tri4b_dnn_mpe/decode_phone_0db/cafe/wer_4_0.0
%WER 39.80 [ 144086 / 362027, 17472 ins, 34781 del, 91833 sub ] exp/tri4b_dnn_dae/decode_phone_0db/white/wer_5_1.0
%WER 11.48 [ 41543 / 362027, 8646 ins, 7906 del, 24991 sub ] exp/tri4b_dnn_dae/decode_phone_0db/car/wer_5_1.0
%WER 30.55 [ 110591 / 362027, 16812 ins, 26292 del, 67487 sub ] exp/tri4b_dnn_dae/decode_phone_0db/cafe/wer_5_1.0
exit 0

for x in exp/{tri4b_dnn_mpe,tri4b_dnn_dae}/decode_word_0db/{white,car,cafe}; do [ -d $x ] && grep WER $x/wer_* | utils/best_wer.sh; done
#clean MPE model and mixture DAE model
#0db noise test data
#word task
%WER 99.43 [ 80680 / 81139, 6 ins, 73931 del, 6743 sub ] exp/tri4b_dnn_mpe/decode_word_0db/white/wer_7_0.0
%WER 27.66 [ 22442 / 81139, 643 ins, 619 del, 21180 sub ] exp/tri4b_dnn_mpe/decode_word_0db/car/wer_8_0.0
%WER 87.76 [ 71209 / 81139, 287 ins, 53511 del, 17411 sub ] exp/tri4b_dnn_mpe/decode_word_0db/cafe/wer_8_0.0
%WER 65.87 [ 53443 / 81139, 864 ins, 4200 del, 48379 sub ] exp/tri4b_dnn_dae/decode_word_0db/white/wer_13_0.0
%WER 25.07 [ 20344 / 81139, 472 ins, 656 del, 19216 sub ] exp/tri4b_dnn_dae/decode_word_0db/car/wer_9_0.0
%WER 51.92 [ 42125 / 81139, 972 ins, 3585 del, 37568 sub ] exp/tri4b_dnn_dae/decode_word_0db/cafe/wer_12_0.0

exit 0
```

这个文件里给出了字错率WER

## x07 模型应用

在s5目录下会有一个exp的目录，




