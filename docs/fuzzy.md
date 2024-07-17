# fuzzy logic (c) Lotfi Zadeh
The fuzzy.py module is a sophisticated toolkit designed for handling fuzzy logic operations, a form of logic that deals with reasoning that is approximate rather than fixed and exact. This module provides a wide range of functions and operations that facilitate the creation of fuzzy systems, making it useful for both theoretical exploration and practical applications. The primary components of this module include functions to transform membership values, membership functions, combinators for fuzzy sets, and classes that define domains, sets, and rules within the fuzzy logic framework.

# Functions to Transform Membership Values
true, false, fairly_false, fairly_true, very_false, very_true

These functions transform a given membership value into a truth value. For instance:

    true(m) returns the membership value itself.
    false(m) returns the inverse of the membership value.
    fairly_false(m) and fairly_true(m) apply transformations that map the membership value onto a part of a circle, providing a geometric interpretation.
    very_false(m) and very_true(m) further extend these geometric transformations.

Functions to Evaluate, Infer, and Defuzzify
round_partial, rescale, weighted_sum

These functions perform various operations on membership values:

    round_partial rounds a value to an arbitrary precision.
    rescale scales a value from one domain to another.
    weighted_sum calculates a weighted sum of membership values, useful for decision trees and similar applications.

# Lingual Hedges
very, plus, minus

Lingual hedges modify the curves of membership values:

    very sharpens memberships, making only values close to 1 stay at the top.
    plus is a milder version of very.
    minus increases membership support so more values reach the top.

# General-Purpose Functions
inv, noop, constant, alpha, normalize, moderate

These functions provide general-purpose operations for membership functions:

    inv inverts a function within the unit interval.
    noop returns the value as is, useful for testing.
    constant returns a fixed value regardless of input.
    alpha clips a function's values within specified bounds.
    normalize maps [0,1] to [0,1] so that the maximum value is 1.
    moderate biases values towards 0.5, damping extremes.

# Membership Functions
singleton, linear, step, bounded_linear, R, S, rectangular, triangular, trapezoid, sigmoid, bounded_sigmoid, bounded_exponential, simple_sigmoid, triangular_sigmoid, gauss

These functions define various types of membership functions used to create fuzzy sets:

    singleton defines a single spike.
    linear creates a linear function with specified gradient and y-intercept.
    step defines a step function with specified limits.
    bounded_linear, R, S, rectangular, triangular, and trapezoid create different types of bounded linear and non-linear functions.
    sigmoid, bounded_sigmoid, bounded_exponential, simple_sigmoid, triangular_sigmoid, and gauss provide more complex membership functions based on sigmoid and Gaussian distributions.

# Combinators for Fuzzy Sets
MIN, MAX, product, bounded_sum, lukasiewicz_AND, lukasiewicz_OR, einstein_product, einstein_sum, hamacher_product, hamacher_sum, lambda_op, gamma_op, simple_disjoint_sum

These combinators define operations for combining fuzzy sets:

    MIN and MAX implement classic AND and OR operations.
    product and bounded_sum provide alternative AND and OR operations.
    lukasiewicz_AND, lukasiewicz_OR, einstein_product, einstein_sum, hamacher_product, and hamacher_sum implement specific combinatory logic operations.
    lambda_op and gamma_op are compensatoric operators that combine AND with OR using a weighing factor.
    simple_disjoint_sum defines a fuzzy XOR operation.

# Domain, Set, and Rule Classes

# Domain

The Domain class defines a measurable dimension of real values, like temperature. It includes methods for defining, accessing, and manipulating fuzzy sets within a domain.

# Set

The Set class defines a fuzzy set within a domain. It includes methods for common fuzzy set operations like AND, OR, NOT, and various hedges. It also provides methods for plotting, array conversion, and calculating the center of gravity.

# Rule

The Rule class defines a collection of bound sets that span a multi-dimensional space of their respective domains. It includes methods for combining rules, evaluating rules based on different methods (like center of gravity), and creating rules from tables.

The fuzzy.py module provides a robust and flexible toolkit for working with fuzzy logic. By incorporating a wide range of functions and operations, it enables the creation of sophisticated fuzzy systems that enhance the capabilities of systems like easyAGI, contributing to the broader field of Augmented Intelligence. This module facilitates both theoretical exploration and practical applications, making it a valuable resource for anyone working with fuzzy logic for advanced reasoning machines.
