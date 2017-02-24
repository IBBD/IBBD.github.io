# 广告点击率预测
翻译自Google的论文《Ad Click Prediction: a View from the Trenches》

## 摘要
点击率预测是一个关联到数十亿美元的在线广告市场的大规模学习问题。从最近的预测系统实验，我们给出一个学习的案例，我们提出`FTRL-Proximal`在线学习算法，这是一种具有良好的稀疏性和收敛性的算法，也是对传统的监督学习算法的改进。

Predicting ad click–through rates (CTR) is a massive-scale learning problem that is central to the multi billion dollar online advertising industry. We present a selection of case studies and topics drawn from recent experiments in the setting of a deployed CTR prediction system. These include improvements in the context of traditional supervised learning based on an FTRL-Proximal online learning algorithm (which has excellent sparsity and convergence properties) and the use of per-coordinate learning rates.

本文也探讨一些在传统机器学习领域可能遇到的问题，例如节省内存的问题，性能评估及其可视化问题，预测结果的置信区间的计算问题，和特征的自动管理问题等。本文最后还会介绍几个方向，这些在其他领域已经取得了可喜的成果，不过在这里还没有相关的证明。本论文突出显示了理论进步和实际工程之间的密切关系，并展示了传统机器学习算法在复杂动态系统中遇到的挑战。

We also explore some of the challenges that arise in a realworld system that may appear at first to be outside the domain of traditional machine learning research. These include useful tricks for memory savings, methods for assessing and visualizing performance, practical methods for providing confidence estimates for predicted probabilities, calibration methods, and methods for automated management of features. Finally, we also detail several directions that did not turn out to be beneficial for us, despite promising results elsewhere in the literature. The goal of this paper is to highlight the close relationship between theoretical advances and practical engineering in this industrial setting, and to show the depth of challenges that appear when applying traditional machine learning methods in a complex dynamic system.

## 1. 介绍
在线广告是一个数十亿美元的产业，一直都是机器学习的成功案例之一。搜索广告，上下文广告，展示类广告，和实时竞价类广告等，都重度依赖于机器学习模型去预测其点击率，以达到更快，更准，更可靠的目标。这也促进了这些领域的发展，即使解决这些规模化的问题在几十年前还是不可思议的。通过使用一个巨大的特征空间，一个典型的工业模型能每天对几十亿的事件进行预测，并且能够根据结果不断提升预测的准确性。

Online advertising is a multi billion dollar industry that has served as one of the great success stories for machine learning. Sponsored search advertising, contextual advertising, display advertising, and realtime bidding auctions have all relied heavily on the ability of learned models to predict ad click–through rates accurately, quickly, and reliably [28, 15, 33, 1, 16]. This problem setting has also pushed the field to address issues of scale that even a decade ago would have been almost inconceivable. A typical industrial model may provide predictions on billions of events per day, using a correspondingly large feature space, and then learn from the resulting mass of data.

在本论文中，通过Google搜索广告的点击率预测系统的实践中，我们提出一系列的案例研究。我们专注的主题虽然有限，但是对于实际运行的系统，那都是非常重要的。因此，我们探讨的问题，例如节省内存，性能分析，置信度预测，特征管理等，都是为了设计一个有效的机器学习算法。论文的目的是为了让读者认识到真实环境中出现的深刻的挑战，也希望这些分享出来的技巧和见解能应用到其他的大规模学习的领域。

In this paper, we present a series of case studies drawn from recent experiments in the setting of the deployed system used at Google to predict ad click–through rates for sponsored search advertising. Because this problem setting is now well studied, we choose to focus on a series of topics that have received less attention but are equally important in a working system. Thus, we explore issues of memory savings, performance analysis, confidence in predictions, calibration, and feature management with the same rigor that is traditionally given to the problem of designing an effective learning algorithm. The goal of this paper is to give the reader a sense of the depth of challenges that arise in real industrial settings, as well as to share tricks and insights that may be applied to other large scale problem areas.

## 2. 系统概述
当用户搜索关键词q时，系统会对待投放广告中广告主设置的关键词进行匹配。然后，拍卖机制就会确定应该将哪些广告展示给用户，按什么顺序进行展示，以及如果广告被点击了，应该按什么价格结算。

When a user does a search q, an initial set of candidate ads is matched to the query q based on advertiser chosen keywords. An auction mechanism then determines whether these ads are shown to the user, what order they are shown in, and what prices the advertisers pay if their ad is clicked.

除了广告主的竞价，对于每一个广告a，其点击概率为`P(click|q, a)`，这就是广告被展示后将会被点击的条件概率。在我们的系统中，包含各种各样的特征，例如搜索关键词，广告创意的文本，以及各种广告相关的元数据。这些特征数据往往都是非常稀疏的，很多情况下都只是有几个非0的特征值。

In addition to the advertiser bids, an important input to the auction is, for each ad a, an estimate of P (click | q, a), the probability that the ad will be clicked if it is shown.  The features used in our system are drawn from a variety of sources, including the query, the text of the ad creative, and various ad-related metadata. Data tends to be extremely sparse, with typically only a tiny fraction of non-zero feature values per example.

一些传统的算法，例如逻辑回归，也是适合用来解决该问题的。它必须能每天进行几十亿次的预测，并且能迅速的根据展示和点击事件更新模型，通常这意味着巨大的训练集。

Methods such as regularized logistic regression are a natural fit for this problem setting. It is necessary to make predictions many billions of times per day and to quickly update the model as new clicks and non-clicks are observed.  Of course, this data rate means that training data sets are enormous. Data is provided by a streaming service based on the Photon system – see [2] for a full discussion.

由于最近几年大规模学习已经被很好的研究过了，这里就不再花大量的篇幅去描述我们的系统架构。然而，我们也注意到，我们提出的是一个单层的学习算法，这Google大脑团队提出的SGD算法不同，那是一个多层的学习算法。这使我们能处理更大的数据集，因为我们更加关注的是数据的稀疏性。

Because large-scale learning has been so well studied in recent years (see [3], for example) we do not devote significant space in this paper to describing our system architecture in detail. We will note, however, that the training methods bear resemblance to the Downpour SGD method described by the Google Brain team [8], with the difference that we train a single-layer model rather than a deep network of many layers. This allows us to handle significantly larger data sets and larger models than have been reported elsewhere to our knowledge, with billions of coefficients. Because trained models are replicated to many data centers for serving (see Figure 1), we are much more concerned with sparsification at serving time rather than during training.

## 3. 在线学习与稀疏性


