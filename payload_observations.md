# Observations of preset payloads

After the (single byte) preset number and (20 byte) preset name, 592 bytes of preset payload remain.

Three main sections of payload are apparent:
* 18 bytes of preset states (enabled,disabled etc.)
* 32 bytes of effect block routing information
* 542 bytes of effect block parameter values


## Preset States
Each effect appears to have two bytes here.
The first represents whether a block is present and enabled (see EFFECT_STATES lookup table),
the second is unknown but has always been zero in observed preset data.

### 000-016 - Effect states
* 000 - gate enable
* 002 - compressor enable
* 004 - filter enable
* 006 - pan + tremolo enable
* 008 - pitch enable
* 010 - delay enable
* 012 - drive enable
* 014 - chorus enable
* 016 - reverb enable

### 018-049 - Routing table
* Table of 32 bytes (8 columns, 4 rows)
* Stored as 8 groups of 4 byte columns
* Each value represents a slot for an effect block (see EFFECT_TYPES lookup table)


## Effect parameters
Each effect block stores parameters in a specific area,
unfortunately each sub-algorithm uses the same space for different parameters.
The settings for gate and output are also stored here.

### 050-055 - Gate parameters
* 050 - gate mode (lookup table)
* 051 - gate threshold (256-x db)
* 052 - gate max damping (x db)
* 053 - gate release rate (x db/s)
* 054 - gate unused in level?
* 055 - gate out level (256-x db)

### 338-351 - Compressor parameters
* 338 - compressor in level (256-x db)
* 339 - compressor out level (256-x db)
* 348 - compressor threshold (256-x db)
* 349 - compressor ratio (lookup table)
* 350 - compressor release (x db/s)
* 351 - compressor knee mode (lookup table)

### 356-387 - filter parameters
* 356 - filter algorithm (lookup table)
* 357 - filter global mix level
* 358 - filter global in level
* 359 - filter global out level
* 360 - filter global mute mode
* 368 - filter parameter
* 369 - filter parameter
* 370 - filter parameter
* 371 - filter parameter
* 372 - filter parameter
* 373 - filter parameter
* 374 - filter parameter
* 375 - filter parameter
* 376 - filter parameter
* 377 - filter parameter
* 378 - filter parameter
* 379 - filter parameter
* 380 - filter parameter
* 381 - filter parameter
* 382 - filter parameter
* 383 - filter parameter
* 384 - filter parameter
* 385 - filter parameter
* 386 - filter parameter
* 387 - filter parameter
* 388 - filter parameter
