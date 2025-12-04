---
title: How the non-destructive readout mode works ?
---

The non-destructive readout mode is activated in the YAML configuration file.

See the following example with **'non-destructive' mode**

With this YAML file:
```yaml
exposure:
  readout:
    times: [10,20,30]
    non_destructive: true    # <====== NON-DESTRUCTIVE MODE !

cmos_detector:
  geometry:
    row: 2
    col: 2
  environment:
  characteristics:
    charge_to_volt_conversion: 3.0e-6
    pre_amplification: 100
    adc_bit_resolution: 16
    adc_voltage_range: [0.,6.]

pipeline:
  charge_generation:
    - name: load_charge
      func: pyxel.models.charge_generation.load_charge
      arguments:
        filename: charge.fits

  charge_collection:
    - name: simple_collection
      func: pyxel.models.charge_collection.simple_collection
      enabled: true

  charge_measurement:
    - name: simple_measurement
      func: pyxel.models.charge_measurement.simple_measurement
      enabled: true

  readout_electronics:
    - name: simple_amplifier
      func: pyxel.models.readout_electronics.simple_amplifier
      enabled: true

    - name: simple_adc
      func: pyxel.models.readout_electronics.simple_adc
      enabled: true
```

and

```python
>>> cfg = pyxel.load("with_non_destructive_mode.yaml")

>>> result = pyxel.run_mode(
    mode=cfg.exposure,
    detector=cfg.detector,
    pipeline=cfg.pipeline,
)
>>> result
DataTree('None', parent=None)
│   Dimensions:  (time: 3, y: 2, x: 2)
│   Coordinates:
│     * y        (y) int64 16B 0 1
│     * x        (x) int64 16B 0 1
│     * time     (time) float64 24B 10.0 20.0 30.0
│   Data variables:
│       photon   (time) float64 24B nan nan nan
│       charge   (time, y, x) float64 96B 10.0 10.0 10.0 10.0 ... 10.0 10.0 10.0   <== Always unchanged
│       pixel    (time, y, x) float64 96B 10.0 10.0 10.0 10.0 ... 30.0 30.0 30.0   <== Pixel are accumulating now
│       signal   (time, y, x) float64 96B 0.003 0.003 0.003 ... 0.009 0.009 0.009
│       image    (time, y, x) uint16 24B 32 32 32 32 65 65 65 65 98 98 98 98
│   Attributes:
│       pyxel version:  2.4.1+16.g2b7e5e0e.dirty
│       running mode:   Exposure
├── DataTree('scene')
└── DataTree('data')
```