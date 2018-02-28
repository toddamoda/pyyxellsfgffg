"""PyXEL Web Server.

TODO
====


DONE: 1. Add 'stop' running pipeline

2. Add port entry field and check box to enable / disable remote
imager communication

DONE: 3. Detector class require refactoring of 'photons' and 'image' so
that it interfaces nicely with GUI.

DONE: 4. Refactor sequencer code to run as an embedded for-loop

5. Implement 'Reset' button. This should reset all entry fields to
YAML file values

6. Gray out the disabled sequencers a bit more. They look enabled.

7. The "set_setting" routine evaluate the string representation of
the object model parameter. This may be problematic latter. Add a
conversion routine (default to literal_eval).

8. Refresh web page should retain collapsed sections and entry field values.

9. Integrate DispatcherBlockingAutoRemoveDeadEndPoints into esapy_dispatcher

DONE: 10. Auto reconnect on button click if websocket had closed
unexpectedly earlier

DONE: 11. Disable "run" button when a pipeline is running.

12. Add button to start esapy_image

13. "random" entry field should be mapped to a numeric quantity.

DONE: 14. Enable a pipeline schema to be selected at runtime from a
dropdown list box.

15. Question: Enable multiple pipelines to be interconnected?

16. Improve error reporting to web interface.

17. Include numpy and logrithmic ranges

18. Include DS9 as viewer.

19. Save current web interface settings to YAML.

20. Add 'enable' attribute to YAML model definitions

21. Add 'seed' value to random number entry fields.

22. output file placeholders.

DONE: 23. integrate JS9.
"""
