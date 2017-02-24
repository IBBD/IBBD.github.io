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
想对于大规模数据集的学习算法，广义的线性模型（如逻辑回归）有很多有很多优点。尽管特征向量`x`可能有数十亿的维度，但是每个是样本通常只会有几百个非0值。这使得从磁盘或者网络来的大规模的流式数据集进行高效的训练成为可能，因为每个训练样本只需要被考虑一次。

For learning at massive scale, online algorithms for generalized linear models (e.g., logistic regression) have many advantages. Although the feature vector x might have billions of dimensions, typically each instance will have only hundreds of nonzero values. This enables efficient training on large data sets by streaming examples from disk or over the network [3], since each training example only needs to be considered once.

（数学符号比较多，直接贴图）
[logistic regression](/_img/ad-click-prediction/logistic-regression.png)

对这些类型的问题，OGD算法已经证明是非常有效的，能用最小的计算资源来获取很好的预测精度。然而，在实践中，另一个需要考虑的关键因素是最终模型的大小，由于可以稀疏地存储模型，w中的非0参数就是内存使用量的决定性因素。

Online gradient descent 1 (OGD) has proved very effective for these kinds of problems, producing excellent prediction accuracy with a minimum of computing resources. However, in practice another key consideration is the size of the final model; since models can be stored sparsely, the number of non-zero coefficients in w is the determining factor of memory usage.

不幸的是，对于稀疏性的数据集，OGD模型并不是那么有效。事实上，只要增加L1参数，就基本上不会产生系数为0的情况了。更复杂的方法，如傅伯斯和截断的梯度成功地引入稀疏[11，20]。相比于FOBOS算法，RDA算法产生更好的精度和稀疏性。然而在我们的数据集上，可以看到梯度下降类算法能比RDA产生更好的精度。于是，问题是我们设计一个算法，同时具备RDA算法的稀疏性和OGD算法的精确性吗？答案是可以的，这就是我们的`FTRL-Proximal`算法。如果不进行正则化，这个算法具有相同的梯度下降，但是因为模型的参数w和L1需要正则化才能更加有效的实现。

Unfortunately, OGD is not particularly effective at producing sparse models. In fact, simply adding a subgradient of the L1 penalty to the gradient of the loss will essentially never produce coefficients that are exactly zero. More sophisticated approaches such as FOBOS and truncated gradient do succeed in introducing sparsity [11, 20]. The Regularized Dual Averaging (RDA) algorithm produces even better accuracy vs sparsity tradeoffs than FOBOS [32]. However, we have observed the gradient-descent style methods can produce better accuracy than RDA on our datasets [24]. The question, then, is can we get both the sparsity provided by RDA and the improved accuracy of OGD? The answer is yes, using the “Follow The (Proximally) Regularized Leader” algorithm, or FTRL-Proximal.  Without regularization, this algorithm is identical to standard online gradient descent, but because it uses an alternative lazy representation of the model coefficients w, L1 regularization can be implemented much more effectively.

下面是模型的数学描述：
[FTRL-Proximal](/_img/ad-click-prediction/ftrl-proximal.png)



