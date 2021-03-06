Tutorial
=======================

We now illustrate the basic capabilities of the ``grmpy`` package.
We start by outlining some basic functional form assumptions before introducing to alternative models that can be used to
estimate the marginal treatment effect (MTE).
We then turn to some simple use cases.

Assumptions
-----------

The ``grmpy`` package implements the normal linear-in-parameters version of the generalized Roy model. Both potential outcomes and the choice :math:`(Y_1, Y_0, D)` are a linear function of the individual's observables :math:`(X, Z)` and random components :math:`(U_1, U_0, V)`.


.. math::
    Y_1  &= X \beta_1 + U_1 \\
    Y_0  &= X \beta_0 + U_0 \\
    D &= I[D^{*} > 0] \\
    D^{*}    &= Z \gamma -V

Individuals decide to select into latent indicator variable :math:`D^{*}` is positive. Depending on their decision, we either observe :math:`Y_1` or :math:`Y_0`.


Parametric Normal Model
^^^^^^^^^^^^^^^^^^^^^^^

The parametric model imposes the assumption of joint normality of the unobservables :math:`(U_1, U_0, V) \sim \mathcal{N}(0, \Sigma)` with mean zero and covariance matrix :math:`\Sigma`.

Semiparametric Model
^^^^^^^^^^^^^^^^^^^^
The semiparametric approach invokes no assumption on the distribution of the unobservables. It requires a weaker condition
:math:`(X,Z) \indep {U_1, U_0, V}`

Under this assumption, the MTE is:

* additively separable in :math:`X` and :math:`U_D`, which means that the shape of the MTE is independent of :math:`X`, and

* identified over the common support of :math:`P(Z)`, unconditional on :math:`X`.


The assumption of common support is crucial for the application of LIV and needs to be carefully evaluated every time.
It is defined as the region where the support of :math:`P(Z)` given :math:`D=1` and the support of :math:`P(Z)` given :math:`D=0 overlap.

Model Specification
-------------------

You can specify the details of the model in an initialization file (`example <https://github.com/OpenSourceEconomics/grmpy/blob/master/docs/tutorial/tutorial.grmpy.yml>`_). This file contains several blocks:

**SIMULATION**

The *SIMULATION* block contains some basic information about the simulation request.

=======     ======      ==============================================
Key         Value       Interpretation
=======     ======      ==============================================
agents      int         number of individuals
seed        int         seed for the specific simulation
source      str         specified name for the simulation output files
=======     ======      ==============================================

**ESTIMATION**

Depending on the model, different input parameters are required.

**PARAMETRIC MODEL**

===========     ======      ===============================================
Key             Value       Interpretation
===========     ======      ===============================================
semipar         False       choose the parametric normal model
agents          int         number of individuals (for the comparison file)
file            str         name of the estimation specific init file
optimizer       str         optimizer used for the estimation process
start           str         flag for the start values
maxiter	        int         maximum numbers of iterations
dependent       str         indicates the dependent variable
indicator       str         label of the treatment indicator variable
output_file     str         name for the estimation output file
comparison	int         flag for enabling the comparison file creation
===========     ======      ===============================================

**SEMIPARAMETRIC MODEL**

=============     ======      =========================================================================================
Key               Value       Interpretation
=============     ======      =========================================================================================
semipar           True        choose the semiparametric model
show_output       bool        If *True*, intermediate outputs of the estimation process are displayed
dependent         str         indicates the dependent variable
indicator         str         label of the treatment indicator variable
file              str         name of the estimation specific init file
logit             bool        If false: probit. Probability model for the choice equation
nbins             int         Number of histogram bins used to determine common support (default is 25)
bandwidth         float       Bandwidth for the locally quadratic regression
gridsize          int         Number of evaluation points for the locally quadratic regression (default is 400)
ps_range          list        Start and end point of the range of :math:`p = u_D` over which the MTE shall be estimated
rbandwidth        int         Bandwidth for the double residual regression (default is 0.05)
trim_support	  bool        Trim the data outside the common support, recommended (default is *True*)
reestimate_p      bool        Re-estimate :math:`P(Z)` after trimming, not recommended (default is *False*)
=============     ======      =========================================================================================

In most empirical applications, bandwidth choices between 0.2 and 0.4 are appropriate.
:cite:`Fan1994` find that a gridsize of 400 is a good default for graphical analysis.
For data sets with less than 400 observations, we recommend a gridsize equivalent to the maximum number of observations that
remain after trimming the common support.
If the data set of size N is large enough, a gridsize of 400 should be considered as the minimal number of evaluation points.
Since *grmpy*'s algorithm is fast enough, gridsize can be easily increased to N evaluation points.

The "rbandwidth", which is 0.05 by default, specifies the bandwidth for the LOESS (Locally Estimated Scatterplot Smoothing) regression of
:math:`X`, :math:`X \ \times \ p`, and :math:`Y` on :math:`\widehat{P}(Z)`. If the sample size is small (N < 400),
the user may need to increase "rbandwidth" to 0.1. Otherwise *grmpy* will throw an error.

Note that the MTE identified by LIV consists of wo components: :math:`\overline{x}(\beta_1 - \beta_0)` (which does not depend on :math:`P(Z) = p`) and :math:`k(p)`
(which does depend on :math:`p`). The latter is estimated nonparametrically. The key "p_range" in the initialization file specifies the interval
over which :math:`k(p)` is estimated. After the data outside the overlapping support are trimmed, the locally quadratic kernel estimator
uses the remaining data to predict :math:`k(p)` over the entire "p_range" specified by the user. If "p_range" is larger than the common support, *grmpy*
extrapolates the values for the MTE outside this region. Technically speaking, interpretations of the MTE are only valid within the common support.
In our empirical applications, we set "p_range" to :math:`[0.005,0.995]`.

The other parameters ("trim_support" and "reestimate_p") are set by default and do not need to be specified by the user.
In rare cases, the user might wish to change these parameters. In general, we do not recommend this.


**TREATED**

The *TREATED* block specifies the number and order of the covariates determining the potential outcome in the treated state
and the values for the coefficients :math:`\beta_1`. Note that the length of the list which determines the parameters has to be equal
to the number of variables that are included in the order list.

=======   =========  ======     ===================================
Key       Container  Values     Interpretation
=======   =========  ======     ===================================
params    list       float      Parameters
order     list       str        Variable labels
=======   =========  ======     ===================================


**UNTREATED**

The *UNTREATED* block specifies the covariates that a the potential outcome in the untreated state and the values for the coefficients :math:`\beta_0`.

=======   =========  ======     ===================================
Key       Container  Values     Interpretation
=======   =========  ======     ===================================
params    list       float      Parameters
order     list       str        Variable labels
=======   =========  ======     ===================================

**CHOICE**

The *CHOICE* block specifies the number and order of the covariates determining the selection process and the values for the coefficients :math:`\gamma`.

=======   =========  ======     ===================================
Key       Container  Values     Interpretation
=======   =========  ======     ===================================
params    list       float      Parameters
order     list       str        Variable labels
=======   =========  ======     ===================================


Further Specifications for the Parametric Model
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**DIST**

The *DIST* block specifies the distribution of the unobservables.

=======   =========  ======     =========================================
Key       Container  Values     Interpretation
=======   =========  ======     =========================================
params    list       float      Upper triangular of the covariance matrix
=======   =========  ======     =========================================

**VARTYPES**

The *VARTYPES* section enables users to specify optional characteristics to specific variables in their simulated data. Currently there is only the option to determine binary variables. For this purpose the user have to specify a key which reflects the corresponding variable label and assign a list to this label which contains the type (*binary*) as a string as well as a float (<0.9) that determines the probability for which the variable is one.

================   =========  ================     =========================================
Key                Container  Values               Interpretation
================   =========  ================     =========================================
*Variable label*   list       string and float     Type of variable + additional information
================   =========  ================     =========================================




**SCIPY-BFGS**

The *SCIPY-BFGS* block contains the specifications for the *BFGS* minimization algorithm. For more information see: `SciPy documentation <https://docs.scipy.org/doc/scipy-0.19.0/reference/optimize.minimize-bfgs.html#optimize-minimize-bfgs>`__.

========  ======      ==================================================================================
Key       Value       Interpretation
========  ======      ==================================================================================
gtol      float       the value that has to be larger as the gradient norm before successful termination
eps       float       value of step size (if *jac* is approximated)
========  ======      ==================================================================================

**SCIPY-POWELL**

The *SCIPY-POWELL* block contains the specifications for the *POWELL* minimization algorithm. For more information see: `SciPy documentation <https://docs.scipy.org/doc/scipy-0.19.0/reference/optimize.minimize-powell.html#optimize-minimize-powell>`__.

========  ======      ===========================================================================
Key       Value       Interpretation
========  ======      ===========================================================================
xtol       float      relative error in solution values *xopt* that is acceptable for convergence
ftol       float      relative error in fun(*xopt*) that is acceptable for convergence
========  ======      ===========================================================================


Examples
--------

Parametric Normal Model
^^^^^^^^^^^^^^^^^^^^^^^

In the following chapter we explore the basic features of the ``grmpy`` package. The resources for the tutorial are also available `online <https://github.com/OpenSourceEconomics/grmpy/tree/master/docs/tutorial>`_.
So far the package provides the features to simulate a sample from the generalized Roy model and to estimate some parameters of interest for a provided sample as specified in your initialization file.

**Simulation**

First we will take a look on the simulation feature. For simulating a sample from the generalized Roy model you use the ``simulate()`` function provided by the package. For simulating a sample of your choice you have to provide the path of your initialization file as an input to the function.
::

    import grmpy

    grmpy.simulate('tutorial.grmpy.yml')


This creates a number of output files that contain information about the resulting simulated sample.

* **data.grmpy.info**, basic information about the simulated sample
* **data.grmpy.txt**, simulated sample in a simple text file
* **data.grmpy.pkl**, simulated sample as a pandas data frame


**Estimation**

The other feature of the package is the estimation of the parameters of interest.
By default, the parametric model is chosen, in which case the parameter *semipar* in the *ESTIMATION* section of the initialization file is set to *False*.
The start values and optimizer options need to be specified in the *ESTIMATION* section.

::

    grmpy.fit('tutorial.grmpy.yml', semipar=False)

As in the simulation process this creates an output files that contain information about the estimation results.


Local Instrumental Variables
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If the user wishes to estimate the parameters of interest using the semiparametric LIV approach, *semipar* must be changed to *True*.

::

    grmpy.fit('tutorial.semipar.yml', semipar=True)

If *show_output* is *True*, ``grmpy`` plots the common support of the propensity score and shows some intermediate outputs of the estimation process.
