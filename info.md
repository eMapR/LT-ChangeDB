common design philosophy, so when you learn how to use one tidyverse package, you learn a lot about how to use the others

## Philosophy

I think R tidyverse sets a great example for how to develop a client library ecosystem

This library attempts to do several things besides provide functions. It is an attempt to provide a template for a common 
client library design that could be used across other client libraries so that when you learn one, using others will
feel similar. 

1. Accept and return the same type of data structure (as input and output)
2. Focus on one task per function
3. Can be combined with other functions to perform multi-step operations
4. verb-noun-(adjective) function names
5. functions that map - create a global variable with defaults, so that other variables besides objects in things
being mapped over are exposed.






When working with data you must:

Figure out what you want to do.

Describe those tasks in the form of a computer program.

Execute the program.

The dplyr package makes these steps fast and easy:

By constraining your options, it helps you think about your data manipulation challenges.

It provides simple “verbs”, functions that correspond to the most common data manipulation tasks, to help you translate your thoughts into code.

It uses efficient backends, so you spend less time waiting for the computer.


verb - a word used to describe an action, state, or occurrence


all functions operate on an ee.ImageCollection and focus on a single task. This mean having to map over the collection
potentially many times to achieve a desired output, but the advantage is flexablity and greater control over the
process. This also allows for chaining multiple steps together.


uses a global dictionary with many properties, this allows for simply function mapping - all of the global properties
are exposed to a given function being mapped.

function names follow a verb-noun pattern where camel case is used to concatentate words, where the first is a verb and the second is noun.
In some cases a third word (adjective for the noun) is included.
This patten describes what the function does and either to what or 

xx = applies to all Landsat data
sr = applies to Landsat surface reflectance
dn = applies to landsat digital number
toa = applies to landsat top of atmosphere
refl = applies to SR and TOA reflectance

## Functions

setProps


* Collection building functions
	- sr.gather*
	- sr.harmonize*
	- xx.exclude
* Transformation functions
	- sdfgsg
* Correction functions
	- ??.correctTopoMinearat
	- xx.correctSLCoff
	- xx.correct
* Masking functions
	- sr.maskFmask*
	- sr.maskOutliers*
	- sr.maskDiff
* Collection assessment functions
	- sr.countValid
	- this
	- that
* Composite functions
	- xx.mosaicPath*
	- xx.mosaicMean
	- xx.mosaicMedian
	- xx.mosaicMedoid
	- xx.mosaicTargetDOY
* Visualization
	- refl.visualize543
	- refl.visualize432
	- refl.visualize321
	- refl.visualizeTC


## Examples
- Count the number of pixels not masked out

- 





