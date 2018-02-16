"""
PyXEL Web Server TODO
=====================


1. Add 'stop' running pipeline

2. Add port entry field and check box to enable / disable remote
imager communication

3. Detector class require refactoring of 'photons' and 'image' so
that it interfaces nicely with GUI.

4. Refactor sequencer code to run as an embedded for-loop

5. Implement 'Reset' button. This should reset all entry fields to
YAML file values

6. Gray out the disabled sequencers a bit more. They look enabled.

7. The "set_setting" routine evaluate the string representation of
the object model parameter. This may be problematic latter. Add a
conversion routine (default to literal_eval).

8. Refresh web page should retain collapsed sections and entry field values.

9. Integrate DispatcherBlockingAutoRemoveDeadEndPoints into esapy_dispatcher

10. Auto reconnect on button click if websocket had closed
unexpectedly earlier

11. Disable "run" button when a pipeline is running.

12. Add button to start esapy_image

13. "random" entry field should be mapped to a numeric quantity.

14. Enable a pipeline schema to be selected at runtime from a
dropdown list box.

15. Question: Enable multiple pipelines to be interconnected?

16. Improve error reporting to web interface.
"""
