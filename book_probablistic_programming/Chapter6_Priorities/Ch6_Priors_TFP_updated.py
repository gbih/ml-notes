#!/usr/bin/env python
# coding: utf-8

# # Probabilistic Programming and Bayesian Methods for Hackers Chapter  6
# 
# <table class="tfo-notebook-buttons" align="left">
#   <td>
#     <a target="_blank" href="https://colab.research.google.com/github/CamDavidsonPilon/Probabilistic-Programming-and-Bayesian-Methods-for-Hackers/blob/master/Chapter6_Priorities/Ch6_Priors_TFP.ipynb"><img height="32px" src="https://colab.research.google.com/img/colab_favicon.ico" />Run in Google Colab</a>
#   </td>
#   <td>
#     <a target="_blank" href="https://github.com/CamDavidsonPilon/Probabilistic-Programming-and-Bayesian-Methods-for-Hackers/blob/master/Chapter6_Priorities/Ch6_Priors_TFP.ipynb"><img src="https://www.tensorflow.org/images/GitHub-Mark-32px.png" />View source on GitHub</a>
#   </td>
# </table>
# <br>
# <br>
# <br>
# 
# Original content ([this Jupyter notebook](https://nbviewer.jupyter.org/github/CamDavidsonPilon/Probabilistic-Programming-and-Bayesian-Methods-for-Hackers/blob/master/Chapter6_Priorities/Ch6_Priors_PyMC2.ipynb)) created by Cam Davidson-Pilon ([`@Cmrn_DP`](https://twitter.com/Cmrn_DP))
# 
# Ported to [Tensorflow Probability](https://www.tensorflow.org/probability/) by Matthew McAteer ([`@MatthewMcAteer0`](https://twitter.com/MatthewMcAteer0)), with help from Bryan Seybold, Mike Shwe ([`@mikeshwe`](https://twitter.com/mikeshwe)), Josh Dillon, and the rest of the TFP team at  Google ([`tfprobability@tensorflow.org`](mailto:tfprobability@tensorflow.org)).
# 
# Welcome to Bayesian Methods for Hackers. The full Github repository is available at [github/Probabilistic-Programming-and-Bayesian-Methods-for-Hackers](https://github.com/CamDavidsonPilon/Probabilistic-Programming-and-Bayesian-Methods-for-Hackers). The other chapters can be found on the project's [homepage](https://camdavidsonpilon.github.io/Probabilistic-Programming-and-Bayesian-Methods-for-Hackers/). We hope you enjoy the book, and we encourage any contributions!
# 
# ---
# ### Table of Contents
# - Dependencies & Prerequisites
# - Getting our priorities straight
#   - Subjective vs Objective priors
#     - Subjective Priors
#   - Decisions, decisions...
#   - Empirical Bayes
# - Useful priors to know about
#   - The Gamma distribution
#   - The Wishart distribution
#   - The Beta distribution
# - Example: Bayesian Multi-Armed Bandits
#   - Applications
#   - A Proposed Solution
#   - A Measure of Good
#   - Extending the algorithm
# - Eliciting expert prior
#   - Trial roulette method
#   - Example: Stock Returns
#   - Protips for the Wishart distribution
# - Conjugate Priors
# - Jeffreys Priors
# - Effect of ther prior as N increases
#   - Bayesian perspective of Penalized Linear Regressions
#     - References
# 
# ---
# 
# This chapter of [Bayesian Methods for Hackers](https://github.com/CamDavidsonPilon/Probabilistic-Programming-and-Bayesian-Methods-for-Hackers) focuses on the most debated and discussed part of Bayesian methodologies: how to choose an appropriate prior distribution. We also present how the prior's influence changes as our dataset increases, and an interesting relationship between priors and penalties on linear regression.

# ### Dependencies & Prerequisites
# 
# <div class="alert alert-success">
#     Tensorflow Probability is part of the colab default runtime, <b>so you don't need to install Tensorflow or Tensorflow Probability if you're running this in the colab</b>. 
#     <br>
#     If you're running this notebook in Jupyter on your own machine (and you have already installed Tensorflow), you can use the following
#     <br>
#       <ul>
#     <li> For the most recent nightly installation: <code>pip3 install -q tfp-nightly</code></li>
#     <li> For the most recent stable TFP release: <code>pip3 install -q --upgrade tensorflow-probability</code></li>
#     <li> For the most recent stable GPU-connected version of TFP: <code>pip3 install -q --upgrade tensorflow-probability-gpu</code></li>
#     <li> For the most recent nightly GPU-connected version of TFP: <code>pip3 install -q tfp-nightly-gpu</code></li>
#     </ul>
# Again, if you are running this in a Colab, Tensorflow and TFP are already installed
# </div>

# In[ ]:


#@title Imports and Global Variables  { display-mode: "form" }
"""
The book uses a custom matplotlibrc file, which provides the unique styles for
matplotlib plots. If executing this book, and you wish to use the book's
styling, provided are two options:
    1. Overwrite your own matplotlibrc file with the rc-file provided in the
       book's styles/ dir. See http://matplotlib.org/users/customizing.html
    2. Also in the styles is  bmh_matplotlibrc.json file. This can be used to
       update the styles in only this notebook. Try running the following code:

        import json
        s = json.load(open("../styles/bmh_matplotlibrc.json"))
        matplotlib.rcParams.update(s)
"""
# get_ipython().system('pip3 install -q pandas_datareader')
# get_ipython().system('pip3 install -q wget')
from __future__ import absolute_import, division, print_function

#@markdown This sets the warning status (default is `ignore`, since this notebook runs correctly)
warning_status = "ignore" #@param ["ignore", "always", "module", "once", "default", "error"]
import warnings
warnings.filterwarnings(warning_status)
with warnings.catch_warnings():
    warnings.filterwarnings(warning_status, category=DeprecationWarning)
    warnings.filterwarnings(warning_status, category=UserWarning)

import numpy as np
import os
#@markdown This sets the styles of the plotting (default is styled like plots from [FiveThirtyeight.com](https://fivethirtyeight.com/))
matplotlib_style = 'fivethirtyeight' #@param ['fivethirtyeight', 'bmh', 'ggplot', 'seaborn', 'default', 'Solarize_Light2', 'classic', 'dark_background', 'seaborn-colorblind', 'seaborn-notebook']
import matplotlib.pyplot as plt; plt.style.use(matplotlib_style)
import matplotlib.axes as axes;
from matplotlib.patches import Ellipse
import scipy.stats as stats
rand = np.random.rand
beta = stats.beta
from mpl_toolkits.mplot3d import Axes3D
import pandas_datareader.data as web
get_ipython().run_line_magic('matplotlib', 'inline')

import seaborn as sns; sns.set_context('notebook')
from IPython.core.pylabtools import figsize
#@markdown This sets the resolution of the plot outputs (`retina` is the highest resolution)
notebook_screen_res = 'retina' #@param ['retina', 'png', 'jpeg', 'svg', 'pdf']
get_ipython().run_line_magic('config', 'InlineBackend.figure_format = notebook_screen_res')

import tensorflow as tf
#tfe = tf.contrib.eager

# Eager Execution
#@markdown Check the box below if you want to use [Eager Execution](https://www.tensorflow.org/guide/eager)
#@markdown Eager execution provides An intuitive interface, Easier debugging, and a control flow comparable to Numpy. You can read more about it on the [Google AI Blog](https://ai.googleblog.com/2017/10/eager-execution-imperative-define-by.html)
#use_tf_eager = False #@param {type:"boolean"}

# Use try/except so we can easily re-execute the whole notebook.
if use_tf_eager:
    try:
        tf.compat.v1.enable_eager_execution()
    except:
        pass

import tensorflow_probability as tfp
tfd = tfp.distributions
tfb = tfp.bijectors

  
def evaluate(tensors):
    """Evaluates Tensor or EagerTensor to Numpy `ndarray`s.
    Args:
    tensors: Object of `Tensor` or EagerTensor`s; can be `list`, `tuple`,
      `namedtuple` or combinations thereof.

    Returns:
      ndarrays: Object with same structure as `tensors` except with `Tensor` or
        `EagerTensor`s replaced by Numpy `ndarray`s.
    """
    if tf.executing_eagerly():
        return tf.nest.pack_sequence_as(
            tensors,
            [t.numpy() if tf.is_tensor(t) else t
             for t in tf.nest.flatten(tensors)])
    return sess.run(tensors)

class _TFColor(object):
    """Enum of colors used in TF docs."""
    red = '#F15854'
    blue = '#5DA5DA'
    orange = '#FAA43A'
    green = '#60BD68'
    pink = '#F17CB0'
    brown = '#B2912F'
    purple = '#B276B2'
    yellow = '#DECF3F'
    gray = '#4D4D4D'
    def __getitem__(self, i):
        return [
            self.red,
            self.orange,
            self.green,
            self.blue,
            self.pink,
            self.brown,
            self.purple,
            self.yellow,
            self.gray,
        ][i % 9]
TFColor = _TFColor()

def session_options(enable_gpu_ram_resizing=True, enable_xla=True):
    """
    Allowing the notebook to make use of GPUs if they're available.
    
    XLA (Accelerated Linear Algebra) is a domain-specific compiler for linear 
    algebra that optimizes TensorFlow computations.
    """
    config = tf.compat.v1.ConfigProto()
    config.log_device_placement = True
    if enable_gpu_ram_resizing:
        # `allow_growth=True` makes it possible to connect multiple colabs to your
        # GPU. Otherwise the colab malloc's all GPU ram.
        config.gpu_options.allow_growth = True
    if enable_xla:
        # Enable on XLA. https://www.tensorflow.org/performance/xla/.
        config.graph_options.optimizer_options.global_jit_level = (
            tf.compat.v1.OptimizerOptions.ON_1)
    return config


def reset_sess(config=None):
    """
    Convenience function to create the TF graph & session or reset them.
    """
    if config is None:
        config = session_options()
    global sess
    tf.compat.v1.reset_default_graph()
    try:
        sess.close()
    except:
        pass
    sess = tf.compat.v1.InteractiveSession(config=config)

reset_sess()


# ## Getting our priorities straight
# 
# 
# Up until now, we have mostly ignored our choice of priors. This is unfortunate as we can be very expressive with our priors, but we also must be careful about choosing them. This is especially true if we want to be objective, that is, not to express any personal beliefs in the priors. 
# 

# ### Subjective vs Objective priors
# 
# Bayesian priors can be classified into two classes: *objective* priors, which aim to allow the data to influence the posterior the most, and *subjective* priors, which allow the practitioner to express his or her views into the prior. 
# 
# What is an example of an objective prior? We have seen some already, including the *flat* prior, which is a uniform distribution over the entire possible range of the unknown. Using a flat prior implies that we give each possible value an equal weighting. Choosing this type of prior is invoking what is called "The Principle of Indifference", literally we have no prior reason to favor one value over another. Calling a flat prior over a restricted space an objective prior is not correct, though it seems similar. If we know $p$ in a Binomial model is greater than 0.5, then $\text{Uniform}(0.5,1)$ is not an objective prior (since we have used prior knowledge) even though it is "flat" over [0.5, 1]. The flat prior must be flat along the *entire* range of possibilities. 
# 
# Aside from the flat prior, other examples of objective priors are less obvious, but they contain important characteristics that reflect objectivity. For now, it should be said that *rarely* is a objective prior *truly* objective. We will see this later.

# #### Subjective Priors
# 
# On the other hand, if we added more probability mass to certain areas of the prior, and less elsewhere, we are biasing our inference towards the unknowns existing in the former area. This is known as a subjective, or *informative* prior. In the figure below, the subjective prior reflects a belief that the unknown likely lives around 0.5, and not around the extremes. The objective prior is insensitive to this.

# In[ ]:


plt.figure(figsize(12.5, 7))

colors = [TFColor[1], TFColor[2], TFColor[3], TFColor[4]]

x = tf.linspace(start=0., stop=1., num=50)
obj_prior_1 = tfd.Beta(1., 1.).prob(x)
subj_prior_1 = tfd.Beta(10., 10.).prob(x)
subj_prior_2 = 2 * tf.ones(25)

[
    x_, obj_prior_1_, subj_prior_1_, subj_prior_2_,
] = evaluate([
    x, obj_prior_1, subj_prior_1, subj_prior_2,
])

p = plt.plot(x_, obj_prior_1_, 
    label='An objective prior \n(uninformative, \n"Principle of Indifference")')
plt.fill_between(x_, 0, obj_prior_1_, color = p[0].get_color(), alpha = 0.3)

p = plt.plot(x_, subj_prior_1_ ,
             label = "A subjective prior \n(informative)")
plt.fill_between(x_, 0, subj_prior_1_, color = p[0].get_color(), alpha = 0.3)

p = plt.plot(x_[25:], subj_prior_2_, 
             label = "another subjective prior")
plt.fill_between(x_[25:], 0, 2, color = p[0].get_color(), alpha = 0.3)

plt.ylim(0,4)

plt.ylim(0, 4)
leg = plt.legend(loc = "upper left")
leg.get_frame().set_alpha(0.4)
plt.title("Comparing objective vs. subjective priors for an unknown probability");


# The choice of a subjective prior does not always imply that we are using the practitioner's subjective opinion: more often the subjective prior was once a posterior to a previous problem, and now the practitioner is updating this posterior with new data. A subjective prior can also be used to inject *domain knowledge* of the problem into the model. We will see examples of these two situations later.

# ### Decision, decisions...
# 
# The choice, either *objective* or *subjective* mostly depends on the problem being solved, but there are a few cases where one is preferred over the other. In instances of scientific research, the choice of an objective prior is obvious. This eliminates any biases in the results, and two researchers who might have differing prior opinions would feel an objective prior is fair. Consider a more extreme situation:
# 
# > A tobacco company publishes a report with a Bayesian methodology that retreated 60 years of medical research on tobacco use. Would you believe the results? Unlikely. The researchers probably chose a subjective prior that too strongly biased results in their favor.
# 
# Unfortunately, choosing an objective prior is not as simple as selecting a flat prior, and even today the problem is still not completely solved. The problem with naively choosing the uniform prior is that pathological issues can arise. Some of these issues are pedantic, but we delay more serious issues to the Appendix of this Chapter.

# We must remember that choosing a prior, whether subjective or objective, is still part of the modeling process. To quote Gelman [5]:
# 
# >... after the model has been fit, one should look at the posterior distribution
# and see if it makes sense. If the posterior distribution does not make sense, this implies
# that additional prior knowledge is available that has not been included in the model,
# and that contradicts the assumptions of the prior distribution that has been used. It is
# then appropriate to go back and alter the prior distribution to be more consistent with
# this external knowledge.
# 
# If the posterior does not make sense, then clearly one had an idea what the posterior *should* look like (not what one *hopes* it looks like), implying that the current prior does not contain all the prior information and should be updated. At this point, we can discard the current prior and choose a more reflective one.
# 
# Gelman [4] suggests that using a uniform distribution with large bounds is often a good choice for objective priors. Although, one should be wary about using Uniform objective priors with large bounds, as they can assign too large of a prior probability to non-intuitive points. Ask yourself: do you really think the unknown could be incredibly large? Often quantities are naturally biased towards 0. A Normal random variable with large variance (small precision) might be a better choice, or an Exponential with a fat tail in the strictly positive (or negative) case. 
# 
# If using a particularly subjective prior, it is your responsibility to be able to explain the choice of that prior, else you are no better than the tobacco company's guilty parties. 

# ### Empirical Bayes
# 
# While not a true Bayesian method, *empirical Bayes* is a trick that combines frequentist and Bayesian inference. As mentioned previously, for (almost) every inference problem there is a Bayesian method and a frequentist method. The significant difference between the two is that Bayesian methods have a prior distribution, with hyperparameters $\alpha$, while empirical methods do not have any notion of a prior. Empirical Bayes combines the two methods by using frequentist methods to select $\alpha$, and then proceeds with Bayesian methods on the original problem. 
# 
# A very simple example follows: suppose we wish to estimate the parameter $\mu$ of a Normal distribution, with $\sigma = 5$. Since $\mu$ could range over the whole real line, we can use a Normal distribution as a prior for $\mu$. How to select the prior's hyperparameters, denoted ($\mu_p, \sigma_p^2$)? The $\sigma_p^2$ parameter can be chosen to reflect the uncertainty we have. For $\mu_p$, we have two options:
# 
# **Option 1**: Empirical Bayes suggests using the empirical sample mean, which will center the prior around the observed empirical mean:
# 
# $$ \mu_p = \frac{1}{N} \sum_{i=0}^N X_i $$
# 
# **Option 2**: Traditional Bayesian inference suggests using prior knowledge, or a more objective prior (zero mean and fat standard deviation).
# 
# Empirical Bayes can be argued as being semi-objective, since while the choice of prior model is ours (hence subjective), the parameters are solely determined by the data.
# 
# Personally, I feel that Empirical Bayes is *double-counting* the data. That is, we are using the data twice: once in the prior, which will influence our results towards the observed data, and again in the inferential engine of MCMC. This double-counting will understate our true uncertainty. To minimize this double-counting, I would only suggest using Empirical Bayes when you have *lots* of observations, else the prior will have too strong of an influence. I would also recommend, if possible, to maintain high uncertainty (either by setting a large $\sigma_p^2$ or equivalent.)
# 
# Empirical Bayes also violates a theoretical axiom in Bayesian inference. The textbook Bayesian algorithm of:
# 
# >*prior* $\Rightarrow$ *observed data* $\Rightarrow$ *posterior* 
# 
# is violated by Empirical Bayes, which instead uses 
# 
# >*observed data* $\Rightarrow$ *prior* $\Rightarrow$ *observed data* $\Rightarrow$ *posterior*
# 
# Ideally, all priors should be specified *before* we observe the data, so that the data does not influence our prior opinions (see the volumes of research by Daniel Kahneman *et. al* about [anchoring](http://en.wikipedia.org/wiki/Anchoring_and_adjustment)).

# ## Useful priors to know about

# ### The Gamma distribution
# 
# A Gamma random variable, denoted $X \sim \text{Gamma}(\alpha, \beta)$, is a random variable over the positive real numbers. It is in fact a generalization of the Exponential random variable, that is:
# 
# $$ \text{Exp}(\beta) \sim \text{Gamma}(1, \beta) $$
# 
# This additional parameter allows the probability density function to have more flexibility, hence allowing the practitioner to express his or her subjective priors more accurately. The density function for a $\text{Gamma}(\alpha, \beta)$ random variable is:
# 
# $$ f(x \mid \alpha, \beta) = \frac{\beta^{\alpha}x^{\alpha-1}e^{-\beta x}}{\Gamma(\alpha)} $$
# 
# where $\Gamma(\alpha)$ is the [Gamma function](http://en.wikipedia.org/wiki/Gamma_function), and for differing values of $(\alpha, \beta)$ looks like:

# In[ ]:


parameters = [(1, 0.5), (9, 2), (3, 0.5), (7, 0.5)]
x = tf.cast(tf.linspace(start=0.001 ,stop=20., num=150), dtype=tf.float32)

plt.figure(figsize(12.5, 7))
for alpha, beta in parameters:
    [ 
        y_, 
        x_ 
    ] = evaluate([
        tfd.Gamma(float(alpha), float(beta)).prob(x), 
        x,
    ])
    lines = plt.plot(x_, y_, label = "(%.1f,%.1f)"%(alpha, beta), lw = 3)
    plt.fill_between(x_, 0, y_, alpha = 0.2, color = lines[0].get_color())
    plt.autoscale(tight=True)

plt.legend(title=r"$\alpha, \beta$ - parameters");


# ### The Wishart distribution
# 
# Until now, we have only seen random variables that are scalars. Of course, we can also have *random matrices*! Specifically, the Wishart distribution is a distribution over all [positive semi-definite matrices](http://en.wikipedia.org/wiki/Positive-definite_matrix). Why is this useful to have in our arsenal? (Proper) covariance matrices are positive-definite, hence the Wishart is an appropriate prior for covariance matrices. We can't really visualize a distribution of matrices, so I'll plot some realizations from the $5 \times 5$ (above) and $20 \times 20$ (below) Wishart distribution:

# In[ ]:


reset_sess()

n = 4
print("output of the eye function \n(a commonly used function with Wishart Distributions): \n", np.eye(n))

plt.figure(figsize(12.5, 7))
for i in range(10):
    ax = plt.subplot(2, 5, i+1)
    if i >= 5:
        n = 15
    [
        wishart_matrices_ 
    ] = evaluate([ 
        tfd.Wishart(df=(n+1), scale=tf.eye(n)).sample() 
    ])
    plt.imshow( wishart_matrices_, 
               interpolation="none", 
               cmap = "hot")
    ax.axis("off")

plt.suptitle("Random matrices from a Wishart Distribution");


# One thing to notice is the symmetry of these matrices. The Wishart distribution can be a little troubling to deal with, but we will use it in an example later.

# ### The Beta distribution
# 
# You may have seen the term `beta` in previous code in this book. Often, I was implementing a Beta distribution. The Beta distribution is very useful in Bayesian statistics. A random variable $X$ has a $\text{Beta}$ distribution, with parameters $(\alpha, \beta)$, if its density function is:
# 
# $$f_X(x | \; \alpha, \beta ) = \frac{ x^{(\alpha - 1)}(1-x)^{ (\beta - 1) } }{B(\alpha, \beta) }$$
# 
# where $B$ is the [Beta function](http://en.wikipedia.org/wiki/Beta_function) (hence the name). The random variable $X$ is only allowed in [0,1], making the Beta distribution a popular distribution for decimal values, probabilities and proportions. The values of $\alpha$ and $\beta$, both positive values, provide great flexibility in the shape of the distribution. Below we plot some distributions:

# In[ ]:


reset_sess()

params = [(2, 5), (1, 1), (0.5, 0.5), (5, 5), (20, 4), (5, 1)]
x = tf.cast(tf.linspace(start=0.01 ,stop=.99, num=100), dtype=tf.float32)

plt.figure(figsize(12.5, 7))
for alpha, beta in params:
    [ 
        y_, 
        x_ 
    ] = evaluate([
        tfd.Beta(float(alpha), float(beta)).prob(x), 
        x,
    ])
    lines = plt.plot(x_, y_, label = "(%.1f,%.1f)"%(alpha, beta), lw = 3)
    plt.fill_between(x_, 0, y_, alpha = 0.2, color = lines[0].get_color())
    plt.autoscale(tight=True)
plt.ylim(0)
plt.legend(title=r"$\alpha, \beta$ - parameters");


# One thing I'd like the reader to notice is the presence of the flat distribution above, specified by parameters $(1,1)$. This is the Uniform distribution. Hence the Beta distribution is a generalization of the Uniform distribution, something we will revisit many times.
# 
# There is an interesting connection between the Beta distribution and the Binomial distribution. Suppose we are interested in some unknown proportion or probability $p$. We assign a $\text{Beta}(\alpha, \beta)$ prior to $p$. We observe some data generated by a Binomial process, say $X \sim \text{Binomial}(N, p)$, with $p$ still unknown. Then our posterior *is again a Beta distribution*, i.e. $p | X \sim \text{Beta}( \alpha + X, \beta + N -X )$. Succinctly, one can relate the two by "a Beta prior with Binomial observations creates a Beta posterior". This is a very useful property, both computationally and heuristically.
# 
# In light of the above two paragraphs, if we start with a $\text{Beta}(1,1)$ prior on $p$ (which is a Uniform), observe data $X \sim \text{Binomial}(N, p)$, then our posterior is $\text{Beta}(1 + X, 1 + N - X)$. 
# 

# ## Example: Bayesian Multi-Armed Bandits
# *Adapted from an example by Ted Dunning of MapR Technologies*
# 
# > Suppose you are faced with $N$ slot machines (colourfully called multi-armed bandits). Each bandit has an unknown probability of distributing a prize (assume for now the prizes are the same for each bandit, only the probabilities differ). Some bandits are very generous, others not so much. Of course, you don't know what these probabilities are. By only choosing one bandit per round, our task is devise a strategy to maximize our winnings.
# 
# Of course, if we knew the bandit with the largest probability, then always picking this bandit would yield the maximum winnings. So our task can be phrased as "Find the best bandit, and as quickly as possible". 
# 
# The task is complicated by the stochastic nature of the bandits. A suboptimal bandit can return many winnings, purely by chance, which would make us believe that it is a very profitable bandit. Similarly, the best bandit can return many duds. Should we keep trying losers then, or give up? 
# 
# A more troublesome problem is, if we have found a bandit that returns *pretty good* results, do we keep drawing from it to maintain our *pretty good score*, or do we try other bandits in hopes of finding an *even-better* bandit? This is the exploration vs. exploitation dilemma.
# 

# ### Applications
# 
# 
# The Multi-Armed Bandit problem at first seems very artificial, something only a mathematician would love, but that is only before we address some applications:
# 
# - Internet display advertising: companies have a suite of potential ads they can display to visitors, but the company is not sure which ad strategy to follow to maximize sales. This is similar to A/B testing, but has the added advantage of naturally minimizing strategies that do not work (and generalizes to A/B/C/D... strategies)
# - Ecology: animals have a finite amount of energy to expend, and following certain behaviours has uncertain rewards. How does the animal maximize its fitness?
# - Finance: which stock option gives the highest return, under time-varying return profiles.
# - Clinical trials: a researcher would like to find the best treatment, out of many possible treatment, while minimizing losses. 
# - Psychology: how does punishment and reward affect our behaviour? How do humans learn?
# 
# Many of these questions above are fundamental to the application's field.
# 
# It turns out the *optimal solution* is incredibly difficult, and it took decades for an overall solution to develop. There are also many approximately-optimal solutions which are quite good. The one I wish to discuss is one of the few solutions that can scale incredibly well. The solution is known as *Bayesian Bandits*.
# 

# ### A Proposed Solution
# 
# 
# Any proposed strategy is called an *online algorithm* (not in the internet sense, but in the continuously-being-updated sense), and more specifically a reinforcement learning algorithm. The algorithm starts in an ignorant state, where it knows nothing, and begins to acquire data by testing the system. As it acquires data and results, it learns what the best and worst behaviours are (in this case, it learns which bandit is the best). With this in mind, perhaps we can add an additional application of the Multi-Armed Bandit problem:
# 
# - Psychology: how does punishment and reward affect our behaviour? How do humans learn?
# 
# 
# The Bayesian solution begins by assuming priors on the probability of winning for each bandit. In our vignette we assumed complete ignorance of these probabilities. So a very natural prior is the flat prior over 0 to 1. The algorithm proceeds as follows:
# 
# For each round:
# 
# 1. Sample a random variable $X_b$ from the prior of bandit $b$, for all $b$.
# 2. Select the bandit with largest sample, i.e. select $B = \text{argmax}\;\; X_b$.
# 3. Observe the result of pulling bandit $B$, and update your prior on bandit $B$.
# 4. Return to 1.
# 
# That's it. Computationally, the algorithm involves sampling from $N$ distributions. Since the initial priors are $\text{Beta}(\alpha=1,\beta=1)$ (a uniform distribution), and the observed result $X$ (a win or loss, encoded 1 and 0 respectfully) is Binomial, the posterior is a $\text{Beta}(\alpha=1+X,\beta=1+1-X)$.
# 
# To answer our question from before, this algorithm suggests that we should not discard losers, but we should pick them at a decreasing rate as we gather confidence that there exist *better* bandits. This follows because there is always a non-zero chance that a loser will achieve the status of $B$, but the probability of this event decreases as we play more rounds (see figure below).
# 
# Below we implement Bayesian Bandits using two classes, `Bandits` that defines the slot machines, and `BayesianStrategy` which implements the above learning strategy.

# In[ ]:


reset_sess()

class Bandits(object):
    """
    This class represents N bandits machines.

    parameters:
        arm_true_payout_probs: a (n,) Numpy array of probabilities >0, <1.

    methods:
        pull( i ): return the results, 0 or 1, of pulling 
                   the ith bandit.
    """
    def __init__(self, arm_true_payout_probs):
        self._arm_true_payout_probs = tf.convert_to_tensor(
              value=arm_true_payout_probs,
              dtype_hint=tf.float32,
              name='arm_true_payout_probs')
        self._uniform = tfd.Uniform(low=0., high=1.)
        assert self._arm_true_payout_probs.shape.is_fully_defined()
        self._shape = np.array(
              self._arm_true_payout_probs.shape.as_list(),
              dtype=np.int32)
        self._dtype = tf.convert_to_tensor(
              value=arm_true_payout_probs,
              dtype_hint=tf.float32).dtype.base_dtype

    @property
    def dtype(self):
        return self._dtype
    
    @property
    def shape(self):
        return self._shape

    def pull(self, arm):
        return (self._uniform.sample(self.shape[:-1]) <
              self._arm_true_payout_probs[..., arm])
    
    def optimal_arm(self):
        return tf.argmax(
            input=self._arm_true_payout_probs,
            axis=-1,
            name='optimal_arm')


# In[ ]:


class BayesianStrategy(object):
    """
    Implements a online, learning strategy to solve
    the Multi-Armed Bandit problem.
    
    parameters:
      bandits: a Bandit class with .pull method
    
    methods:
      sample_bandits(n): sample and train on n pulls.
    """
    
    def __init__(self, bandits):
        self.bandits = bandits
        dtype = bandits._dtype
        self.wins_var = tf.Variable(
            initial_value=tf.zeros(self.bandits.shape, dtype))
        self.trials_var = tf.Variable(
            initial_value=tf.zeros(self.bandits.shape, dtype))
      
    def sample_bandits(self, n=1):
        return tf.while_loop(
            cond=lambda *args: True,
            body=self._one_trial,
            loop_vars=(tf.identity(self.wins_var),
                       tf.identity(self.trials_var)),
            maximum_iterations=n,
            parallel_iterations=1)
    
    def make_posterior(self, wins, trials):
        return tfd.Beta(concentration1=1. + wins,
                        concentration0=1. + trials - wins)
        
    def _one_trial(self, wins, trials):
        # sample from the bandits's priors, and select the largest sample
        rv_posterior_payout = self.make_posterior(wins, trials)
        posterior_payout = rv_posterior_payout.sample()
        choice = tf.argmax(input=posterior_payout, axis=-1)

        # Update trials.
        one_hot_choice = tf.reshape(
            tf.one_hot(
                indices=tf.reshape(choice, shape=[-1]),
                depth=self.bandits.shape[-1],
                dtype=self.trials_var.dtype.base_dtype),
            shape=tf.shape(input=wins))
        trials = tf.compat.v1.assign_add(self.trials_var, one_hot_choice)

        # Update wins.
        result = self.bandits.pull(choice)
        update = tf.compat.v1.where(result, one_hot_choice, tf.zeros_like(one_hot_choice))
        wins = tf.compat.v1.assign_add(self.wins_var, update)

        return wins, trials


# Below we visualize the learning of the Bayesian Bandit solution.

# In[ ]:


reset_sess()

hidden_prob_ = np.array([0.85, 0.60, 0.75])
bandits = Bandits(hidden_prob_)
bayesian_strat = BayesianStrategy(bandits)


draw_samples_ = np.array([1, 1, 3, 10, 10, 25, 50, 100, 200, 600])

def plot_priors(bayesian_strategy, prob, wins, trials, 
                lw = 3, alpha = 0.2, plt_vlines = True):
    ## plotting function
    for i in range(prob.shape[0]):
        posterior_dists = tf.cast(tf.linspace(start=0.001 ,stop=.999, num=200), dtype=tf.float32)
        y = tfd.Beta(concentration1 = tf.cast((1+wins[i]), dtype=tf.float32) , 
                     concentration0 = tf.cast((1 + trials[i] - wins[i]), dtype=tf.float32))
        y_prob_i = y.prob(tf.cast(prob[i], dtype=tf.float32))
        y_probs = y.prob(tf.cast(posterior_dists, dtype=tf.float32))
        [ 
            posterior_dists_,
            y_probs_,
            y_prob_i_,
        ] = evaluate([
            posterior_dists, 
            y_probs,
            y_prob_i,
        ])
        
        p = plt.plot(posterior_dists_, y_probs_, lw = lw)
        c = p[0].get_markeredgecolor()
        plt.fill_between(posterior_dists_, y_probs_,0, color = c, alpha = alpha, 
                         label="underlying probability: %.2f" % prob[i])
        if plt_vlines:
            plt.vlines(prob[i], 0, y_prob_i_ ,
                       colors = c, linestyles = "--", lw = 2)
        plt.autoscale(tight = "True")
        plt.title("Posteriors After %d pull" % N_pulls +                    "s"*(N_pulls > 1))
        plt.autoscale(tight=True)
    return

plt.figure(figsize(11.0, 12))
for j,i in enumerate(draw_samples_):
    plt.subplot(5, 2, j+1) 
    evaluate(tf.compat.v1.global_variables_initializer())
    [wins_, trials_] = evaluate(bayesian_strat.sample_bandits(i))
    N_pulls = int(draw_samples_.cumsum()[j])
    plot_priors(bayesian_strat, hidden_prob_, wins=wins_, trials=trials_)
    #plt.legend()
    plt.autoscale(tight = True)
plt.tight_layout()


# Note that we don't really care how accurate we become about the inference of the hidden probabilities &mdash; for this problem we are more interested in choosing the best bandit (or more accurately, becoming *more confident* in choosing the best bandit). For this reason, the distribution of the red bandit is very wide (representing ignorance about what that hidden probability might be) but we are reasonably confident that it is not the best, so the algorithm chooses to ignore it.
# 
# From the above, we can see that after 1000 pulls, the majority of the "blue" function leads the pack, hence we will almost always choose this arm. This is good, as this arm is indeed the best.
# 
# Below is a D3 app that demonstrates our algorithm updating/learning three bandits.  The first figure are the raw counts of pulls and wins, and the second figure is a dynamically updating plot. I encourage you to try to guess which bandit is optimal, prior to revealing the true probabilities, by selecting the `arm buttons`.

# In[ ]:


# Getting the HTML file for the simulated Bayesian Bandits
reset_sess()

import wget
url = 'https://raw.githubusercontent.com/CamDavidsonPilon/Probabilistic-Programming-and-Bayesian-Methods-for-Hackers/master/Chapter6_Priorities/BanditsD3.html'
filename = wget.download(url)
filename


# In[ ]:


from IPython.core.display import HTML

#try executing the below command twice if the first time doesn't work
HTML(filename = "BanditsD3.html")


# Deviations of the observed ratio from the highest probability is a measure of performance. For example, in the long run, we can attain the reward/pull ratio of the maximum bandit probability if we are optimal. Long-term realized ratios less than the maximum represent inefficiencies. (Realized ratios larger than the maximum probability is due to randomness, and will eventually fall below). 
# 
# ### A Measure of *Good*
# 
# We need a metric to calculate how well we are doing. Recall the absolute *best* we can do is to always pick the bandit with the largest probability of winning. Denote this best bandit's probability by $w_{opt}$. Our score should be relative to how well we would have done had we chosen the best bandit from the beginning. This motivates the *total regret* of a strategy, defined:
# $$
# \begin{align}
# R_T & = \sum_{i=1}^{T} \left( w_{opt} - w_{B(i)} \right)\\
# & = Tw^* - \sum_{i=1}^{T} \;  w_{B(i)} 
# \end{align}
# $$
# 
# where $w_{B(i)}$ is the probability of a prize of the chosen bandit in the $i$ round. A total regret of 0 means the strategy is matching the best possible score. This is likely not possible, as initially our algorithm will often make the wrong choice.  Ideally, a strategy's total regret should flatten as it learns the best bandit. (Mathematically, we achieve $w_{B(i)}=w_{opt}$ often)
# 
# 
# Below we plot the total regret of this simulation, including the scores of some other strategies:
# 
# 1. Random: randomly choose a bandit to pull. If you can't beat this, just stop. 
# 2. Largest Bayesian credible bound: pick the bandit with the largest upper bound in its 95% credible region of the underlying probability. 
# 3. Bayes-UCB algorithm: pick the bandit with the largest *score*, where score is a dynamic quantile of the posterior (see [4] )
# 4. Mean of posterior: choose the bandit with the largest posterior mean. This is what a human player (sans computer) would likely do. 
# 5. Largest proportion: pick the bandit with the current largest observed proportion of winning. 
# 
# The code for these are in the `other_strats.py`, where you can implement your own very easily.
# 

# In[ ]:


url = 'https://raw.githubusercontent.com/CamDavidsonPilon/Probabilistic-Programming-and-Bayesian-Methods-for-Hackers/master/Chapter6_Priorities/other_strats.py'
filename = wget.download(url)
filename


# In[ ]:


plt.figure(figsize(12.5, 5))
from other_strats import *

#define a harder problem
hidden_prob = np.array([0.15, 0.2, 0.1, 0.05])
bandits = Bandits(hidden_prob)

#define regret
def regret(probabilities, choices):
    w_opt = probabilities.max()
    return (w_opt - probabilities[choices.astype(int)]).cumsum()

#create new strategies
strategies= [upper_credible_choice, 
            bayesian_bandit_choice, 
            ucb_bayes , 
            max_mean,
            random_choice]
algos = []
for strat in strategies:
    algos.append(GeneralBanditStrat(bandits, strat))
    
#train 10000 times
for strat in algos:
    strat.sample_bandits(10000)
    
#test and plot
for i,strat in enumerate(algos):
    _regret = regret(hidden_prob, strat.choices)
    plt.plot(_regret, label = strategies[i].__name__, lw = 3)

plt.title(r"Total Regret of Bayesian Bandits Strategy vs. Random guessing")
plt.xlabel(r"Number of pulls")
plt.ylabel(r"Regret after $n$ pulls");
plt.legend(loc = "upper left");


# Like we wanted, Bayesian bandits and other strategies have decreasing rates of regret, representing we are achieving optimal choices. To be more scientific so as to remove any possible luck in the above simulation, we should instead look at the *expected total regret*:
# 
# $$\bar{R}_T = E[ R_T ] $$
# 
# It can be shown that any *sub-optimal* strategy's expected total regret is bounded below logarithmically. Formally,
# 
# $$ E[R_T] = \Omega \left( \;\log(T)\; \right) $$
# 
# Thus, any strategy that matches logarithmic-growing regret is said to "solve" the Multi-Armed Bandit problem [3].
# 
# Using the Law of Large Numbers, we can approximate Bayesian Bandit's expected total regret by performing the same experiment many times (500 times, to be fair):

# In[ ]:


# This can be slow, so I recommend NOT running it.
# Estimated time for Graph Mode: 16 minutes.

trials = tf.constant(500)
expected_total_regret = tf.zeros((10000, 3))

[
    trials_,
    expected_total_regret_,
] = evaluate([
    trials,
    expected_total_regret,
])

for i_strat, strat in enumerate(strategies[:-2]):
    for i in range(trials_):
        general_strat = GeneralBanditStrat(bandits, strat)
        general_strat.sample_bandits(10000)
        _regret = regret(hidden_prob, general_strat.choices)
        expected_total_regret_[:,i_strat] += _regret
    plt.plot(expected_total_regret_[:,i_strat]/trials_, lw =3, label = strat.__name__)
        
plt.title("Expected Total Regret of Multi-armed Bandit strategies")
plt.xlabel("Number of pulls")
plt.ylabel("Exepected Total Regret \n after $n$ pulls");
plt.legend(loc = "upper left");


# In[ ]:


# This cell is dependent on the previous one
# If you didn't run the previous one, you don't have to run this one
plt.figure()

[pl1, pl2, pl3] = plt.plot(expected_total_regret_[:, [0,1,2]], lw = 3)

plt.xscale("log")
plt.legend([pl1, pl2, pl3], 
           ["Upper Credible Bound", "Bayesian Bandit", "UCB-Bayes"],
            loc="upper left")
plt.ylabel(r"Exepected Total Regret after $\log{n}$ pulls");
plt.title( r"log-scale of above" );
plt.ylabel(r"Exepected Total Regret after $\log{n}$ pulls");


# ### Extending the algorithm 
# 
# 
# Because of the Bayesian Bandits algorithm's simplicity, it is easy to extend. Some possibilities:
# 
# - If interested in the *minimum* probability (eg: where prizes are a bad thing), simply choose $B = \text{argmin} \; X_b$ and proceed.
# 
# - Adding learning rates: Suppose the underlying environment may change over time. Technically the standard Bayesian Bandit algorithm would self-update itself (awesome) by noting that what it thought was the best is starting to fail more often. We can motivate the algorithm to learn changing environments quicker by simply adding a *rate* term upon updating:
# 
#         self.wins[choice] = rate*self.wins[choice] + result
#         self.trials[choice] = rate*self.trials[choice] + 1
# 
#    If `rate < 1`, the algorithm will *forget* its previous wins quicker and there will be a downward  pressure towards ignorance. Conversely, setting `rate > 1` implies your algorithm will act more risky, and bet on earlier winners more often and be more resistant to changing environments. 
# 
# - Hierarchical algorithms: We can setup a Bayesian Bandit algorithm on top of smaller bandit algorithms. Suppose we have $N$ Bayesian Bandit models, each varying in some behavior (for example  different `rate` parameters, representing varying sensitivity to changing environments). On top of these $N$ models is another Bayesian Bandit learner that will select a sub-Bayesian Bandit. This chosen Bayesian Bandit will then make an internal choice as to which machine to pull. The super-Bayesian Bandit updates itself depending on whether the sub-Bayesian Bandit was correct or not. 
# 
# - Extending the rewards, denoted $y_a$ for bandit $a$, to random variables from a distribution $f_{y_a}(y)$ is straightforward. More generally, this problem can be rephrased as "Find the bandit with the largest expected value", as playing the bandit with the largest expected value is optimal. In the case above, $f_{y_a}$ was Bernoulli with probability $p_a$, hence the expected value for a bandit is equal to $p_a$, which is why it looks like we are aiming to maximize the probability of winning. If $f$ is not Bernoulli, and it is non-negative, which can be accomplished apriori by shifting the distribution (we assume we know $f$), then the algorithm behaves as before:
# 
#    For each round, 
#     
#    1. Sample a random variable $X_b$ from the prior of bandit $b$, for all $b$.
#    2. Select the bandit with largest sample, i.e. select bandit $B = \text{argmax}\;\; X_b$.
#    3. Observe the result,$R \sim f_{y_a}$, of pulling bandit $B$, and update your prior on bandit $B$.
#    4. Return to 1
# 
#    The issue is in the sampling of $X_b$ drawing phase. With Beta priors and Bernoulli observations, we have a Beta posterior &mdash; this is easy to sample from. But now, with arbitrary distributions $f$, we have a non-trivial posterior. Sampling from these can be difficult.
# 
# - There has been some interest in extending the Bayesian Bandit algorithm to commenting systems. Recall in Chapter 4, we developed a ranking algorithm based on the Bayesian lower-bound of the proportion of upvotes to total votes. One problem with this approach is that it will bias the top rankings towards older comments, since older comments naturally have more votes (and hence the lower-bound is tighter to the true proportion). This creates a positive feedback cycle where older comments gain more votes, hence are displayed more often, hence gain more votes, etc. This pushes any new, potentially better comments, towards the bottom. J. Neufeld proposes a system to remedy this that uses a Bayesian Bandit solution.
# 
# His proposal is to consider each comment as a Bandit, with the number of pulls equal to the number of votes cast, and number of rewards as the number of upvotes, hence creating a $\text{Beta}(1+U,1+D)$ posterior. As visitors visit the page, samples are drawn from each bandit/comment, but instead of displaying the comment with the $\max$ sample, the comments are ranked according to the ranking of their respective samples. From J. Neufeld's blog [6]:
# 
#    > [The] resulting ranking algorithm is quite straightforward, each new time the comments page is loaded, the score for each comment is sampled from a $\text{Beta}(1+U,1+D)$, comments are then ranked by this score in descending order... This randomization has a unique benefit in that even untouched comments $(U=1,D=0)$ have some chance of being seen even in threads with 5000+ comments (something that is not happening now), but, at the same time, the user is not likely to be inundated with rating these new comments. 

# Just for fun, though the colors explode, we watch the Bayesian Bandit algorithm learn 15 different options. 

# In[ ]:


# To avoid any conflicts with our 'other_strats.py' contents, we re-define our
# classes here so you can run this notebook in one 'run all' call
class Bandits(object):
    """
    This class represents N bandits machines.

    parameters:
        arm_true_payout_probs: a (n,) Numpy array of probabilities >0, <1.

    methods:
        pull( i ): return the results, 0 or 1, of pulling 
                   the ith bandit.
    """
    def __init__(self, arm_true_payout_probs):
        self._arm_true_payout_probs = tf.convert_to_tensor(
            value=arm_true_payout_probs,
            dtype_hint=tf.float32,
            name='arm_true_payout_probs')
        self._uniform = tfd.Uniform(low=0., high=1.)
        assert self._arm_true_payout_probs.shape.is_fully_defined()
        self._shape = np.array(
            self._arm_true_payout_probs.shape.as_list(),
            dtype=np.int32)
        self._dtype = self._arm_true_payout_probs.dtype.base_dtype

    @property
    def dtype(self):
        return self._dtype
    
    @property
    def shape(self):
        return self._shape

    def pull(self, arm):
        return (self._uniform.sample(self.shape[:-1]) <
                self._arm_true_payout_probs[..., arm])
    
    def optimal_arm(self):
        return tf.argmax(
            input=self._arm_true_payout_probs,
            axis=-1,
            name='optimal_arm')
    
class BayesianStrategy(object):
    """
    Implements a online, learning strategy to solve
    the Multi-Armed Bandit problem.
    
    parameters:
      bandits: a Bandit class with .pull method
    
    methods:
      sample_bandits(n): sample and train on n pulls.
    """
    
    def __init__(self, bandits):
        self.bandits = bandits
        dtype = self.bandits.dtype.base_dtype
        self.wins_var = tf.Variable(
            initial_value=tf.zeros(self.bandits.shape, dtype))
        self.trials_var = tf.Variable(
            initial_value=tf.zeros(self.bandits.shape, dtype))
      
    def sample_bandits(self, n=1):
        return tf.while_loop(
            cond=lambda *args: True,
            body=self._one_trial,
            loop_vars=(tf.identity(self.wins_var),
                       tf.identity(self.trials_var)),
            maximum_iterations=n,
            parallel_iterations=1)
    
    def make_posterior(self, wins, trials):
        return tfd.Beta(concentration1=1. + wins,
                        concentration0=1. + trials - wins)
        
    def _one_trial(self, wins, trials):
        # sample from the bandits's priors, and select the largest sample
        rv_posterior_payout = self.make_posterior(wins, trials)
        posterior_payout = rv_posterior_payout.sample()
        choice = tf.argmax(input=posterior_payout, axis=-1)

        # Update trials.
        one_hot_choice = tf.reshape(
            tf.one_hot(
                indices=tf.reshape(choice, shape=[-1]),
                depth=self.bandits.shape[-1],
                dtype=self.trials_var.dtype.base_dtype),
            shape=tf.shape(input=wins))
        trials = tf.compat.v1.assign_add(self.trials_var, one_hot_choice)

        # Update wins.
        result = self.bandits.pull(choice)
        update = tf.compat.v1.where(result, one_hot_choice, tf.zeros_like(one_hot_choice))
        wins = tf.compat.v1.assign_add(self.wins_var, update)

        return wins, trials


# In[ ]:


# Now we run our code
plt.figure(figsize(12.0, 8))

hidden_prob = tfd.Beta(1., 13.).sample(sample_shape = (35))
[ hidden_prob_ ] = evaluate([ hidden_prob ])
print(hidden_prob_)
bandits = Bandits(hidden_prob_)
bayesian_strat = BayesianStrategy(bandits)

draw_samples_2 = tf.constant([100, 200, 500, 1300])
[draw_samples_2_] = evaluate([draw_samples_2])

for j,i in enumerate(draw_samples_2_):
    plt.subplot(2, 2, j+1) 
    evaluate(tf.compat.v1.global_variables_initializer())
    [wins_, trials_] = evaluate(bayesian_strat.sample_bandits(i))
    N_pulls = int(draw_samples_2_.cumsum()[j])
    plot_priors(bayesian_strat, hidden_prob_, wins=wins_, trials=trials_,
                lw = 2, alpha = 0.0, plt_vlines=False)
    plt.xlim(0, 0.5)


# ## Eliciting expert prior
# 
# Specifying a subjective prior is how practitioners incorporate domain knowledge about the problem into our mathematical framework. Allowing domain knowledge is useful for many reasons:
# 
# - Aids speeds of MCMC convergence. For example, if we know the unknown parameter is strictly positive, then we can restrict our attention there, hence saving time that would otherwise be spent exploring negative values.
# - More accurate inference. By weighing prior values near the true unknown value higher, we are narrowing our eventual inference (by making the posterior tighter around the unknown) 
# - Express our uncertainty better. See the *Price is Right* problem in Chapter 5.
# 
# plus many other reasons. Of course, practitioners of Bayesian methods are not experts in every field, so we must turn to domain experts to craft our priors. We must be careful with how we elicit these priors though. Some things to consider:
# 
# 1. From experience, I would avoid introducing Betas, Gammas, etc. to non-Bayesian practitioners. Furthermore, non-statisticians can get tripped up by how a continuous probability function can have a value exceeding one.
# 
# 2. Individuals often neglect the rare *tail-events* and put too much weight around the mean of distribution. 
# 
# 3. Related to above is that almost always individuals will under-emphasize the uncertainty in their guesses.
# 
# Eliciting priors from non-technical experts is especially difficult. Rather than introduce the notion of probability distributions, priors, etc. that may scare an expert, there is a much simpler solution. 

# 
# 
# ### Trial roulette method 
# 
# 
# The *trial roulette method* [7] focuses on building a prior distribution by placing counters (think casino chips) on what the expert thinks are possible outcomes. The expert is given $N$ counters (say $N=20$) and is asked to place them on a pre-printed grid, with bins representing intervals.  Each column would represent their belief of the probability of getting the corresponding bin result. Each chip would represent an $\frac{1}{N} = 0.05$ increase in the probability of the outcome being in that interval. For example [8]:
# 
# > A student is asked to predict the mark in a future exam. The figure below shows a completed grid for the elicitation of a subjective probability distribution. The horizontal axis of the grid shows the possible bins (or mark intervals) that the student was asked to consider. The numbers in top row record the number of chips per bin. The completed grid (using a total of 20 chips) shows that the student believes there is a 30% chance that the mark will be between 60 and 64.9.
# 
# 
# From this, we can fit a distribution that captures the expert's choice. Some reasons in favor of using this technique are:
# 
# 1. Many questions about the shape of the expert's subjective probability distribution can be answered without the need to pose a long series of questions to the expert - the statistician can simply read off density above or below any given point, or that between any two points.
# 
# 2. During the elicitation process, the experts can move around the chips if unsatisfied with the way they placed them initially - thus they can be sure of the final result to be submitted.
# 
# 3. It forces the expert to be coherent in the set of probabilities that are provided. If all the chips are used, the probabilities must sum to one.
# 
# 4. Graphical methods seem to provide more accurate results, especially for participants with modest levels of statistical sophistication.

# ### Example: Stock Returns
# 
# 
# Take note stock brokers: you're doing it wrong. When choosing which stocks to pick, an analyst will often look at the *daily return* of the stock. Suppose $S_t$ is the price of the stock on day $t$, then the daily return on day $t$ is :
# 
# $$r_t = \frac{ S_t - S_{t-1} }{ S_{t-1} } $$
# 
# The *expected daily return* of a stock is denoted $\mu = E[ r_t ]$. Obviously, stocks with high expected returns are desirable. Unfortunately, stock returns are so filled with noise that it is very hard to estimate this parameter. Furthermore, the parameter might change over time (consider the rises and falls of AAPL stock), hence it is unwise to use a large historical dataset. 
# 
# Historically, the expected return has been estimated by using the sample mean. This is a bad idea. As mentioned, the sample mean of a small sized dataset has enormous potential to be very wrong (again, see Chapter 4 for full details). Thus Bayesian inference is the correct procedure here, since we are able to see our uncertainty along with probable values.
# 
# For this exercise, we will be examining the daily returns of the AAPL, GOOG, MSFT and AMZN. Before we pull in the data, suppose we ask our a stock fund manager (an expert in finance, but see [9] ), 
# 
# > What do you think the return profile looks like for each of these companies?
# 
# Our stock broker, without needing to know the language of Normal distributions, or priors, or variances, etc. creates four distributions using the trial roulette method above. Suppose they look enough like Normals, so we fit Normals to them. They may look like: 

# In[ ]:


plt.figure(figsize(11., 7))
colors = [TFColor[3], TFColor[0], TFColor[6], TFColor[2]]

expert_prior_params_ = {"GOOG":(-0.03, 0.04), 
                        "AAPL":(0.05, 0.03), 
                        "AMZN": (0.03, 0.02), 
                        "TSLA": (-0.02, 0.01),}

for i, (name, params) in enumerate(expert_prior_params_.items()):
    x = tf.linspace(start=-0.15, stop=0.15, num=100)
    plt.subplot(2, 2, i+1)
    y = tfd.Normal(loc=params[0], scale = params[1]).prob(x)
    [ x_, y_ ] = evaluate([ x, y ])
    plt.fill_between(x_, 0, y_, color = colors[i], linewidth=2,
                     edgecolor = colors[i], alpha = 0.6)
    plt.title(name + " prior")
    plt.vlines(0, 0, y_.max(), "k","--", linewidth = 0.5)
    plt.xlim(-0.15, 0.15)
plt.tight_layout()


# Note that these are subjective priors: the expert has a personal opinion on the stock returns of each of these companies, and is expressing them in a distribution. He's not wishful thinking -- he's introducing domain knowledge.
# 
# In order to better model these returns, we should investigate the *covariance matrix* of the returns. For example, it would be unwise to invest in two stocks that are highly correlated, since they are likely to tank together (hence why fund managers suggest a diversification strategy). We will use the *Wishart distribution* for this, introduced earlier.

# Let's get some historical data for these stocks. We will use the covariance of the returns as a starting point for our Wishart random variable. This is not empirical bayes (as we will go over later) because we are only deciding the starting point, not influencing the parameters.

# In[ ]:


#@title External Stock Data
import datetime
import collections
import pandas_datareader.data as web
import pandas as pd

n_observations = 100 #@param {type:"slider", min:50, max:200, step:10}
#@markdown We will truncate the the most recent 100 days by default.
stock_1 = "GOOG" #@param {type:"string"}
stock_2 = "AAPL" #@param {type:"string"}
stock_3 = "AMZN" #@param {type:"string"}
stock_4 = "TSLA" #@param {type:"string"}
stocks = [stock_1, stock_2, stock_3, stock_4]

start_date = "2015-09-01" #@param {type:"date"}
end_date = "2018-04-27" #@param {type:"date"}

CLOSE = 2

stock_closes = pd.DataFrame()

for stock in stocks:
    stock_data = web.DataReader(stock,'yahoo', start_date, end_date)
    dates = stock_data.index.values
    x = np.array(stock_data)
    stock_series = pd.Series(x[1:,CLOSE].astype(float), name=stock)
    stock_closes[stock] = stock_series
    
stock_closes = stock_closes[::-1]
stock_returns = stock_closes.pct_change()[1:][-n_observations:]
dates = dates[-n_observations:]
stock_returns_obs = stock_returns.values.astype(dtype=np.float32)
print (stock_returns[:10])


# And here let's form our basic model:

# In[ ]:


expert_prior_mu = tf.constant([x[0] for x in expert_prior_params_.values()], dtype=tf.float32)
expert_prior_std = tf.constant([x[1] for x in expert_prior_params_.values()], dtype=tf.float32)

true_mean = tf.cast(stock_returns.mean(), dtype=tf.float32)
print("Observed Mean Stock Returns: \n", evaluate(true_mean),"\n")
true_covariance = tf.cast(stock_returns.cov().values, dtype=tf.float32)
print("\n Observed Stock Returns Covariance matrix: \n", evaluate(true_covariance))


# Here are the returns for our chosen stocks:

# In[ ]:


plt.figure(figsize(12.5, 4))

cum_returns = np.cumprod(1 + stock_returns) - 1
cum_returns.index = dates#[::-1]
cum_returns.plot()

plt.legend(loc = "upper left")
plt.title("Return space")
plt.ylabel("Return of $1 on first date, x100%");


# In[ ]:


plt.figure(figsize(11., 7))

for i, _stock in enumerate(stocks):
    plt.subplot(2,2,i+1)
    plt.hist(stock_returns[_stock], bins=20,
             normed = True, histtype="stepfilled",
             color=colors[i], alpha=0.7)
    plt.title(_stock + " returns")
    plt.xlim(-0.15, 0.15)

plt.tight_layout()
plt.suptitle("Histogram of daily returns", size =14);


# Below we perform the inference on the posterior mean return and posterior covariance matrix. 

# In[ ]:


def stock_joint_log_prob(observations, prior_mu, prior_scale_diag, loc, scale_tril):
    """MVN with priors: loc=Normal, covariance=Wishart.

    Args:
      observations: `[n, d]`-shaped `Tensor` representing Bayesian Gaussian
        Mixture model draws. Each sample is a length-`d` vector.
      prior_mu: Expert Prior Mu
      prior_scale_diag: Expert Prior scale (diagonal)
      loc: `[K, d]`-shaped `Tensor` representing the location parameter of the
        `K` components.
      scale_tril: `[K, d, d]`-shaped `Tensor` representing `K` lower
        triangular `cholesky(Covariance)` matrices, each being sampled from
        a Wishart distribution.

    Returns:
      log_prob: `Tensor` representing joint log-density over all inputs.
    """
    rv_loc = tfd.MultivariateNormalDiag(loc=prior_mu,
                                        scale_identity_multiplier=1.)
    rv_cov = tfd.Wishart(
        df=10,
        # scale_tril = chol(diag(prior_scale_diag**2)) is equivalent to
        scale_tril=tf.linalg.tensor_diag(prior_scale_diag),  
        # For computational reasons, let's make all calcultions in Cholesky form.
        input_output_cholesky=True)  
    rv_observations = tfd.MultivariateNormalTriL(
        loc=loc,
        scale_tril=scale_tril)
    return (rv_loc.log_prob(loc) +
            rv_cov.log_prob(scale_tril) +
            tf.reduce_sum(input_tensor=rv_observations.log_prob(observations), axis=-1))
          


# In[ ]:


num_results = 30000
num_burnin_steps = 5000


# Set the chain's start state.
initial_chain_state = [
    expert_prior_mu,
    tf.linalg.tensor_diag(expert_prior_std),
]

# Set the unconstraining bijectors.
unconstraining_bijectors = [
    tfb.Identity(),
# Maps between a positive-definite matrix and a numerically stabilized, 
# lower-triangular form.
    tfb.ScaleTriL() 
]

# Define a closure over our joint_log_prob.
unnormalized_posterior_log_prob = lambda *args: stock_joint_log_prob(
    stock_returns_obs, expert_prior_mu, expert_prior_std, *args)

# Initialize the step_size. (It will be automatically adapted.)
with tf.compat.v1.variable_scope(tf.compat.v1.get_variable_scope(), reuse=tf.compat.v1.AUTO_REUSE):
    step_size = tf.compat.v1.get_variable(
    name='stock_step_size',
    initializer=tf.constant(0.5, dtype=tf.float32),
    trainable=False,
    use_resource=True
)

kernel=tfp.mcmc.TransformedTransitionKernel(
    inner_kernel=tfp.mcmc.HamiltonianMonteCarlo(
    target_log_prob_fn=unnormalized_posterior_log_prob,
    num_leapfrog_steps=2,
    step_size=step_size,
    state_gradients_are_stopped=True),
    # Since HMC operates over unconstrained space, we need to transform
    # the samples so they live in real-space.
    bijector=unconstraining_bijectors)

kernel = tfp.mcmc.SimpleStepSizeAdaptation(
    inner_kernel=kernel, num_adaptation_steps=int(num_burnin_steps * 0.8))


# Sample from the chain.
[
    stock_return_samples,
    chol_covariance_samples,
], kernel_results = tfp.mcmc.sample_chain(
      num_results=num_results,
      num_burnin_steps=num_burnin_steps,
      current_state=initial_chain_state,
      kernel=kernel)

mean_chol_covariance = tf.reduce_mean(input_tensor=chol_covariance_samples, axis=0)

# Initialize any created variables.
init_g = tf.compat.v1.global_variables_initializer()


# In[ ]:


# Can take up to 1 minute in Graph Mode
evaluate(init_g)
[
    stock_return_samples_,
    chol_covariance_samples_,
    mean_chol_covariance_,
    kernel_results_
] = evaluate([
    stock_return_samples,
    chol_covariance_samples,
    mean_chol_covariance,
    kernel_results
])
print("acceptance rate: {}".format(
    kernel_results_.inner_results.inner_results.is_accepted.mean()))

print("final step size: {}".format(
    kernel_results_.new_step_size[-100:].mean()))


# In[ ]:


plt.figure(figsize(12.5, 4))

# examine the mean return first.
# mean_return_samples_ is a 4-column data frame collected for each stock
mu_samples_ = stock_return_samples_

for i in range(4):
    plt.hist(mu_samples_[:,i], alpha = 0.8 - 0.05*i, bins = 30,
             histtype="stepfilled", color=colors[i], density=True, 
             label = "%s" % stock_returns.columns[i])

plt.vlines(mu_samples_.mean(axis=0), 0, 500, linestyle="--", linewidth = .5)

plt.title(r"Posterior distribution of $\mu$, daily stock returns")
plt.xlim(-0.010, 0.010)
plt.legend();


# (Plots like these are what inspired the book's cover.)
# 
# What can we say about the results above? Clearly TSLA has been a strong performer because the distribution is mostly above zero. Similarly, most of the distribution of AMZN is negative, suggesting that its *true daily return* is negative.
# 
# You may not have immediately noticed, but these variables are a whole order of magnitude *less* than our priors on them. For example, to put these on the same scale as the above prior distributions:

# In[ ]:


plt.figure(figsize(11.0, 7))

for i in range(4):
    plt.subplot(2,2,i+1)
    plt.hist(mu_samples_[:,i], alpha = 0.8 - 0.05*i, bins = 30,
             histtype="stepfilled", density=True, color = colors[i],
             label = "%s" % stock_returns.columns[i])
    plt.title("%s" % stock_returns.columns[i])
    plt.xlim(-0.15, 0.15)
    
plt.suptitle(r"Posterior distribution of daily stock returns")
plt.tight_layout()


# Why did this occur? Recall how I mentioned that finance has a very very low signal to noise ratio. This implies an environment where inference is much more difficult. One should be careful about over-interpreting these results: notice (in the first figure) that each distribution is positive at 0, implying that the stock may return nothing. Furthermore, the subjective priors influenced the results. From the fund managers point of view, this is good as it reflects his updated beliefs about the stocks, whereas from a neutral viewpoint this can be too subjective of a result.  
# 
# Below we show the posterior correlation matrix, and posterior standard deviations. An important caveat to know is that the Wishart distribution models the *covariance matrix* (although it can also be used to model the inverse covariance matrix). We also normalize the matrix to acquire the *correlation matrix*. Since we cannot plot hundreds of matrices effectively, we settle by summarizing the posterior distribution of correlation matrices by showing the *mean posterior correlation matrix* (defined on line 2).

# In[ ]:


mean_covariance_matrix = tf.matmul(mean_chol_covariance_, mean_chol_covariance_, adjoint_b=True)
mean_covariance_matrix_ = evaluate(mean_covariance_matrix)

def cov2corr(A):
    """
      A: covariance matrix input
    Returns:
      A:  correlation matrix output
    """
    d = tf.sqrt(tf.linalg.diag_part(A))
    A = tf.transpose(a=tf.transpose(a=A)/d)/d
    return A


plt.subplot(1,2,1)
plt.imshow(evaluate(cov2corr(mean_covariance_matrix_)) , interpolation="none", 
                cmap = "hot") 
plt.xticks(evaluate(tf.range(4.)), stock_returns.columns)
plt.yticks(evaluate(tf.range(4.)), stock_returns.columns)
plt.colorbar(orientation="vertical")
plt.title("(mean posterior) Correlation Matrix")

plt.subplot(1,2,2)
plt.bar(evaluate(tf.range(4.)), evaluate(tf.sqrt(tf.linalg.diag_part(mean_covariance_matrix_))),
        color = "#5DA5DA", alpha = 0.7)
plt.xticks(evaluate(tf.range(4.)), stock_returns.columns);
plt.title("(mean posterior) standard deviations of daily stock returns")

plt.tight_layout();


# Looking at the above figures, we can say that likely TSLA has an above-average volatility (looking at the return graph this is quite clear). The correlation matrix shows that there are not strong correlations present, except perhaps GOOG and AMZN expressing a much higher correlation of about 0.80; if you look back a few cells at the original plot of the returns over time, you'll see how closely they follow each other.
# 
# With this Bayesian analysis of the stock market, we can throw it into a Mean-Variance optimizer (which I cannot stress enough, do not use with frequentist point estimates) and find the minimum. This optimizer balances the tradeoff between a high return and high variance.
# 
# $$ w_\text{opt} = \max_{w} \frac{1}{N}\left( \sum_{i=0}^N \mu_i^T w - \frac{\lambda}{2}w^T\Sigma_i w \right)$$
# 
# where $\mu_i$ and $\Sigma_i$ are the $i$th posterior estimate of the mean returns and the covariance matrix. This is another example of loss function optimization.

# ### Protips for the Wishart distribution
# 
# If you plan to be using the Wishart distribution, read on. Else, feel free to skip this. 
# 
# In the problem above, the Wishart distribution behaves pretty nicely. Unfortunately, this is rarely the case. The problem is that estimating an $NxN$ covariance matrix involves estimating $\frac{1}{2}N(N-1)$ unknowns. This is a large number even for modest $N$. Personally, I've tried performing a similar simulation as above with $N = 23$ stocks, and ended up giving up considering that I was requesting my MCMC simulation to estimate at least $\frac{1}{2}23*22 = 253$ additional unknowns (plus the other interesting unknowns in the problem). This is not easy for MCMC. Essentially, you are asking you MCMC to traverse 250+ dimensional space. And the problem seemed so innocent initially! Below are some tips, in order of supremacy:
# 
# 1. Use conjugancy if it applies. See section below.
# 
# 2. Use a good starting value. What might be a good starting value? Why, the data's sample covariance matrix is! Note that this is not empirical Bayes: we are not touching the prior's parameters, we are modifying the starting value of the MCMC. Due to numerical instability, it is best to truncate the floats in the sample covariance matrix down a few degrees of precision (e.g. while TFP holds up to instability and unsymmetrical matrices much better than higher-level tools like PyMC, it's stilll better to try and avoid them for the sake of model accuracy). 
# 
# 3. Provide as much domain knowledge in the form of priors, if possible. I stress *if possible*. It is likely impossible to have an estimate about each $\frac{1}{2}N(N-1)$ unknown. In this case, see number 4.
# 
# 4. Use empirical Bayes, i.e. use the sample covariance matrix as the prior's parameter.
# 
# 5. For problems where $N$ is very large, nothing is going to help. Instead, ask, do I really care about *every* correlation? Probably not. Further ask yourself, do I really really care about correlations? Possibly not. In finance, we can set an informal hierarchy of what we might be interested in the most: first a good estimate of $\mu$, the variances along the diagonal of the covariance matrix are secondly important, and finally the correlations are least important. So, it might be better to ignore the $\frac{1}{2}(N-1)(N-2)$ correlations and instead focus on the more important unknowns.
# 
# **Another thing** to note is that Wishart distribution matrices are required to have certain mathematical characteristics that are very restrictive. This makes it so that it is impossible for MCMC methods to propose matrices that will be accepted in our sampling procedure. With our model here we sample the Bartlett decomposition of a Wishart distribution matrix and use that to calculate our samples for the covariance matrix (http://en.wikipedia.org/wiki/Wishart_distribution#Bartlett_decomposition).

# ## Conjugate Priors
# 
# Recall that a $\text{Beta}$ prior with $\text{Binomial}$ data implies a $\text{Beta}$ posterior. Graphically:
# 
# $$ \underbrace{\text{Beta}}_{\text{prior}} \cdot \overbrace{\text{Binomial}}^{\text{data}} = \overbrace{\text{Beta}}^{\text{posterior} } $$ 
# 
# Notice the $\text{Beta}$ on both sides of this equation (no, you cannot cancel them, this is not a *real* equation). This is a really useful property. It allows us to avoid using MCMC, since the posterior is known in closed form. Hence inference and analytics are easy to derive. This shortcut was the heart of the  Bayesian Bandit algorithm above. Fortunately, there is an entire family of distributions that have similar behaviour.  
# 
# Suppose $X$ comes from, or is believed to come from, a well-known distribution, call it $f_{\alpha}$, where $\alpha$ are possibly unknown parameters of $f$. $f$ could be a Normal distribution, or Binomial distribution, etc. For particular distributions $f_{\alpha}$, there may exist a prior distribution $p_{\beta}$, such that:
# 
# $$ \overbrace{p_{\beta}}^{\text{prior}} \cdot \overbrace{f_{\alpha}(X)}^{\text{data}} = \overbrace{p_{\beta'}}^{\text{posterior} } $$ 
# 
# where $\beta'$ is a different set of parameters *but $p$ is the same distribution as the prior*. A prior $p$ that satisfies this relationship is called a *conjugate prior*. As I mentioned, they are useful computationally, as we can avoided approximate inference using MCMC and go directly to the posterior. This sounds great, right?
# 
# Unfortunately, not quite. There are a few issues with conjugate priors.
# 
# 1. The conjugate prior is not objective. Hence only useful when a subjective prior is required. It is not guaranteed that the conjugate prior can accommodate the practitioner's subjective opinion.
# 
# 2. There typically exist conjugate priors for simple, one dimensional problems. For larger problems, involving more complicated structures, hope is lost to find a conjugate prior. For smaller models, Wikipedia has a nice [table of conjugate priors](http://en.wikipedia.org/wiki/Conjugate_prior#Table_of_conjugate_distributions).
# 
# Really, conjugate priors are only useful for their mathematical convenience: it is simple to go from prior to posterior. I personally see conjugate priors as only a neat mathematical trick, and offer little insight into the problem at hand. 

# ## Jefferys Priors
# 
# Earlier, we talked about objective priors rarely being *objective*. Partly what we mean by this is that we want a prior that doesn't bias our posterior estimates. The flat prior seems like a reasonable choice as it assigns equal probability to all values. 
# 
# But the flat prior is not transformation invariant. What does this mean? Suppose we have a random variable $\textbf X$ from Bernoulli($\theta$). We define the prior on $p(\theta) = 1$. 

# In[ ]:


plt.figure(figsize(12.5, 5))

x = tf.linspace(start=0.000 ,stop=1, num=150)
y = tf.linspace(start=1.0, stop=1.0, num=150)

[
    x_, y_
] = evaluate([
    x, y
])

lines = plt.plot(x_, y_, color=TFColor[0], lw = 3)
plt.fill_between(x_, 0, y_, alpha = 0.2, color = lines[0].get_color())
plt.autoscale(tight=True)
plt.ylim(0, 2);


# Now, let's transform $\theta$ with the function $\psi = \log \frac{\theta}{1-\theta}$. This is just a function to stretch $\theta$ across the real line. Now how likely are different values of $\psi$ under our transformation.

# In[ ]:


plt.figure(figsize(12.5, 5))

psi = tf.linspace(start=-10. ,stop=10., num=150)
y = tf.exp(psi) / (1 + tf.exp(psi))**2
    
[psi_, y_] = evaluate([psi, y])
    
lines = plt.plot(psi_, y_, color=TFColor[0], lw = 3)
plt.fill_between(psi_, 0, y_, alpha = 0.2, color = lines[0].get_color())
plt.autoscale(tight=True)
plt.ylim(0, 1);


# Oh no! Our function is no longer flat. It turns out flat priors do carry information in them after all. The point of Jeffreys Priors is to create priors that don't accidentally become informative when you transform the variables you placed them originally on.
# 
# Jeffreys Priors are defined as:
# 
# $$p_J(\theta) \propto \mathbf{I}(\theta)^\frac{1}{2}$$
# $$\mathbf{I}(\theta) = - \mathbb{E}\bigg[\frac{d^2 \text{ log } p(X|\theta)}{d\theta^2}\bigg]$$
# 
# $\mathbf{I}$ being the *Fisher information*

# ## Effect of the prior as $N$ increases
# 
# In the first chapter, I proposed that as the amount of our observations or data increases, the influence of the prior decreases. This is intuitive. After all, our prior is based on previous information, and eventually enough new information will shadow our previous information's value. The smothering of the prior by enough data is also helpful: if our prior is significantly wrong, then the self-correcting nature of the data will present to us a *less wrong*, and eventually *correct*, posterior. 
# 
# We can see this mathematically. First, recall Bayes Theorem from Chapter 1 that relates the prior to the posterior. The following is a sample from [What is the relationship between sample size and the influence of prior on posterior?](http://stats.stackexchange.com/questions/30387/what-is-the-relationship-between-sample-size-and-the-influence-of-prior-on-poste)[1] on CrossValidated.
# 
# >The posterior distribution for a parameter $\theta$, given a data set ${\textbf X}$ can be written as 
# 
# $$p(\theta | {\textbf X}) \propto \underbrace{p({\textbf X} | \theta)}_{{\textrm likelihood}}  \cdot  \overbrace{ p(\theta) }^{ {\textrm prior} }  $$
# 
# 
# 
# >or, as is more commonly displayed on the log scale, 
# 
# $$ \log( p(\theta | {\textbf X})  ) = c + L(\theta;{\textbf X}) + \log(p(\theta)) $$
# 
# >The log-likelihood, $L(\theta;{\textbf X}) = \log \left( p({\textbf X}|\theta) \right)$, **scales with the sample size**, since it is a function of the data, while the prior density does not. Therefore, as the sample size increases, the absolute value of $L(\theta;{\textbf X})$ is getting larger while $\log(p(\theta))$ stays fixed (for a fixed value of $\theta$), thus the sum $L(\theta;{\textbf X}) + \log(p(\theta))$ becomes more heavily influenced by $L(\theta;{\textbf X})$ as the sample size increases. 
# 
# There is an interesting consequence not immediately apparent. As the sample size increases, the chosen prior has less influence. Hence inference converges regardless of chosen prior, so long as the areas of non-zero probabilities are the same. 
# 
# Below we visualize this. We examine the convergence of two posteriors of a Binomial's parameter $\theta$, one with a flat prior and the other with a biased prior towards 0. As the sample size increases, the posteriors, and hence the inference, converge.

# In[ ]:


p = 0.6
beta1_params = tf.constant([1.,1.])
beta2_params = tf.constant([2,10])


data = tfd.Bernoulli(probs=p).sample(sample_shape=(500))
[
    beta1_params_, 
    beta2_params_, 
    data_,
] = evaluate([
    beta1_params, 
    beta2_params, 
    data
])

plt.figure(figsize(12.5, 15))
plt.figure()
for i, N in enumerate([0, 4, 8, 32, 64, 128, 500]):
    s = data_[:N].sum() 
    plt.subplot(8,1,i+1)
    params1 = beta1_params_ + np.array([s, N-s])
    params2 = beta2_params_ + np.array([s, N-s])
    x = tf.linspace(start=0.00, stop=1., num=125)
    y1 = tfd.Beta(concentration1 = tf.cast(params1[0], dtype=tf.float32), 
                  concentration0 = tf.cast(params1[1], dtype=tf.float32)).prob(tf.cast(x, dtype=tf.float32))
    y2 = tfd.Beta(concentration1 = tf.cast(params2[0], dtype=tf.float32), 
                  concentration0 = tf.cast(params2[1], dtype=tf.float32)).prob(tf.cast(x, dtype=tf.float32))
    [x_, y1_, y2_] = evaluate([x, y1, y2])
    plt.plot(x_, y1_, label = r"flat prior", lw =3)
    plt.plot(x_, y2_, label = "biased prior", lw= 3)
    plt.fill_between(x_, 0, y1_, color ="#5DA5DA", alpha = 0.15) 
    plt.fill_between(x_, 0, y2_, color ="#F15854", alpha = 0.15) 
    plt.legend(title = "N=%d" % N)
    plt.vlines(p, 0.0, 7.5, linestyles = "--", linewidth=1)
    plt.ylim( 0, 20)


# Keep in mind, not all posteriors will "forget" the prior this quickly. This example was just to show that *eventually* the prior is forgotten. The "forgetfulness" of the prior as we become awash in more and more data is the reason why Bayesian and Frequentist inference eventually converge as well.

# ### Bayesian perspective of Penalized Linear Regressions
# 
# There is a very interesting relationship between a penalized least-squares regression and Bayesian priors. A penalized linear regression is a optimization problem of the form:
# 
# $$ \text{argmin}_{\beta} \;\; (Y - X\beta)^T(Y - X\beta)  + f(\beta)$$
# 
# for some function $f$ (typically a norm like $|| \cdot ||_p^p$). 
# 
# We will first describe the probabilistic interpretation of least-squares linear regression. Denote our response variable $Y$, and features are contained in the data matrix $X$. The standard linear model is:
# 
# \begin{equation}
# Y = X\beta + \epsilon
# \end{equation}
# 
# where $\epsilon \sim \text{Normal}( {\textbf 0}, \sigma{\textbf I })$. Simply, the observed $Y$ is a linear function of $X$ (with coefficients $\beta$) plus some noise term. Our unknown to be determined is $\beta$. We use the following property of Normal random variables:
# 
# $$ \mu' + \text{Normal}( \mu, \sigma ) \sim \text{Normal}( \mu' + \mu , \sigma ) $$
# 
# to rewrite the above linear model as:
# $$
# \begin{align}
# & Y = X\beta + \text{Normal}( {\textbf 0}, \sigma{\textbf I }) \\
# & Y = \text{Normal}( X\beta , \sigma{\textbf I }) \\
# \end{align}
# $$
# In probabilistic notation, denote $f_Y(y \; | \; \beta )$ the probability distribution of $Y$, and recalling the density function for a Normal random variable (see [here](http://en.wikipedia.org/wiki/Normal_distribution) ):
# 
# $$ f_Y( Y \; |\; \beta, X) = L(\beta|\; X,Y)= \frac{1}{\sqrt{ 2\pi\sigma} } \exp \left( \frac{1}{2\sigma^2} (Y - X\beta)^T(Y - X\beta) \right) $$
# 
# This is the likelihood function for $\beta$. Taking the $\log$:
# 
# $$ \ell(\beta) = K - c(Y - X\beta)^T(Y - X\beta) $$
# 
# where $K$ and $c>0$ are constants. Maximum likelihood techniques wish to maximize this for $\beta$, 
# 
# $$\hat{ \beta } = \text{argmax}_{\beta} \;\; - (Y - X\beta)^T(Y - X\beta) $$
# 
# Equivalently we can *minimize the negative* of the above:
# 
# $$\hat{ \beta } = \text{argmin}_{\beta} \;\; (Y - X\beta)^T(Y - X\beta) $$
# 
# This is the familiar least-squares linear regression equation. Therefore we showed that the solution to a linear least-squares is the same as the maximum likelihood assuming Normal noise. Next we extend this to show how we can arrive at penalized linear regression by a suitable choice of prior on $\beta$. 
# 
# 

# #### Penalized least-squares
# 
# In the above, once we have the likelihood, we can include a prior distribution on $\beta$ to derive to the equation for the posterior distribution:
# 
# $$P( \beta | Y, X ) = L(\beta|\;X,Y)p( \beta )$$
# 
# where $p(\beta)$ is a prior on the elements of $\beta$. What are some interesting priors? 
# 
# 1\. If we include *no explicit* prior term, we are actually including an uninformative prior, $P( \beta ) \propto 1$, think of it as uniform over all numbers. 
# 
# 2\. If we have reason to believe the elements of $\beta$ are not too large, we can suppose that *a priori*:
# 
# $$ \beta \sim \text{Normal}({\textbf 0 }, \lambda {\textbf I } ) $$
# 
# The resulting posterior density function for $\beta$ is *proportional to*:
# 
# $$ \exp \left( \frac{1}{2\sigma^2} (Y - X\beta)^T(Y - X\beta) \right) \exp \left( \frac{1}{2\lambda^2} \beta^T\beta \right) $$
# 
# and taking the $\log$ of this, and combining and redefining constants, we arrive at:
# 
# $$ \ell(\beta) \propto K -  (Y - X\beta)^T(Y - X\beta) - \alpha \beta^T\beta  $$
# 
# we arrive at the function we wish to maximize (recall the point that maximizes the posterior distribution is the MAP, or *maximum a posterior*):
# 
# $$\hat{ \beta } = \text{argmax}_{\beta} \;\; -(Y - X\beta)^T(Y - X\beta) - \alpha \;\beta^T\beta $$
# 
# Equivalently, we can minimize the negative of the above, and rewriting $\beta^T \beta = ||\beta||_2^2$:
# 
# $$\hat{ \beta } = \text{argmin}_{\beta} \;\; (Y - X\beta)^T(Y - X\beta) + \alpha \;||\beta||_2^2$$
# 
# This above term is exactly Ridge Regression. Thus we can see that ridge regression corresponds to the MAP of a linear model with Normal errors and a Normal prior on $\beta$.
# 
# 3\. Similarly, if we assume a *Laplace* prior on $\beta$, ie. 
# 
# $$ f_\beta( \beta) \propto \exp \left(- \lambda ||\beta||_1 \right)$$
# 
# and following the same steps as above, we recover:
# 
# $$\hat{ \beta } = \text{argmin}_{\beta} \;\; (Y - X\beta)^T(Y - X\beta) + \alpha \;||\beta||_1$$
# 
# which is LASSO regression. Some important notes about this equivalence. The sparsity that is a result of using a LASSO regularization is not a result of the prior assigning high probability to sparsity. Quite the opposite actually. It is the combination of the $|| \cdot ||_1$ function and using the MAP that creates sparsity on $\beta$: [purely a geometric argument](http://camdp.com/blogs/least-squares-regression-l1-penalty). The prior does contribute to an overall shrinking of the coefficients towards 0 though. An interesting discussion of this can be found in [2].
# 
# For an example of Bayesian linear regression, see Chapter 4's example on financial losses.

# ## References
# 
# [1] Macro, . "What is the relationship between sample size and the influence of prior on posterior?." 13 Jun 2013. StackOverflow, Online Posting to Cross-Validated. Web. 25 Apr. 2013.
# 
# [2] Starck, J.-L., , et al. "Sparsity and the Bayesian Perspective." Astronomy & Astrophysics. (2013): n. page. Print.
# 
# [3] Kuleshov, Volodymyr, and Doina Precup. "Algorithms for the multi-armed bandit problem." Journal of Machine Learning Research. (2000): 1-49. Print.
# 
# [4] Gelman, Andrew. "Prior distributions for variance parameters in hierarchical models." Bayesian Analysis. 1.3 (2006): 515-533. Print.
# 
# [5] Gelman, Andrew, and Cosma R. Shalizi. "Philosophy and the practice of Bayesian statistics." British Journal of Mathematical and Statistical Psychology. (2012): n. page. Web. 17 Apr. 2013.
# 
# [6] James, Neufeld. "Reddit's "best" comment scoring algorithm as a multi-armed bandit task." Simple ML Hacks. Blogger, 09 Apr 2013. Web. 25 Apr. 2013.
# 
# [7] Oakley, J. E., Daneshkhah, A. and O’Hagan, A. Nonparametric elicitation using the roulette method. Submitted to Bayesian Analysis.
# 
# [8] "Eliciting priors from experts." 19 Jul 2010. StackOverflow, Online Posting to Cross-Validated. Web. 1 May. 2013. <http://stats.stackexchange.com/questions/1/eliciting-priors-from-experts>.
# 
# [9] Taleb, Nassim Nicholas (2007), The Black Swan: The Impact of the Highly Improbable, Random House, ISBN 978-1400063512

# In[ ]:


from IPython.core.display import HTML
def css_styling():
    styles = open("../styles/custom.css", "r").read()
    return HTML(styles)
css_styling()

