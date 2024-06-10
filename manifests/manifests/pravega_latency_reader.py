#!/usr/bin/env python3

#
# Copyright (c) Dell Inc., or its subsidiaries. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#

import logging
import signal
import time
import traceback
import argparse
import distutils.util
import gi
from gi.repository import GLib, Gst
gi.require_version("Gst", "1.0")
gi.require_version("GLib", "2.0")


# Log file to output latency values.
latency_log = open("./latency-log.log", "a")
latency_log.write("absolute_time(s),experiment_time(s),e2e latency(ms)\n")
initial_time = time.time()

def bus_call(bus, message, loop):
    """Callback for GStreamer bus messages"""
    t = message.type
    if t == Gst.MessageType.EOS:
        logging.info("End-of-stream")
        loop.quit()
    elif t == Gst.MessageType.WARNING:
        err, debug = message.parse_warning()
        logging.warning("%s: %s" % (err, debug))
    elif t == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        logging.error("%s: %s" % (err, debug))
        loop.quit()
    elif t == Gst.MessageType.ELEMENT:
        details = message.get_structure().to_string()
        logging.info("%s: %s" % (message.src.name, str(details),))
    elif t == Gst.MessageType.PROPERTY_NOTIFY:
        details = message.get_structure().to_string()
        logging.debug("%s: %s" % (message.src.name, str(details),))
    return True


def format_clock_time(ns):
    """Format time in nanoseconds like 01:45:35.975000000"""
    s, ns = divmod(ns, 1000000000)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return "%u:%02u:%02u.%09u" % (h, m, s, ns)


def add_probe(pipeline, element_name, callback, pad_name="sink", probe_type=Gst.PadProbeType.BUFFER):
    logging.info("add_probe: Adding probe to %s pad of %s" % (pad_name, element_name))
    element = pipeline.get_by_name(element_name)
    if not element:
        raise Exception("Unable to get element %s" % element_name)
    sinkpad = element.get_static_pad(pad_name)
    if not sinkpad:
        raise Exception("Unable to get %s pad of %s" % (pad_name, element_name))
    sinkpad.add_probe(probe_type, callback, 0)


def show_metadata_probe(pad, info, user_data):
    """Buffer probe to show metadata in a buffer"""
    gst_buffer = info.get_buffer()
    if gst_buffer:
        time_nanosec = time.time_ns()
        logging.info("show_metadata_probe: %20s:%-8s: pts=%23s, e2e lantecy(ms)=%s, dts=%23s, duration=%23s, size=%8d" % (
            pad.get_parent_element().name,
            pad.name,
            format_clock_time(gst_buffer.pts),
            ((time_nanosec - (gst_buffer.pts - 37000000000)) / 1000000.),
            format_clock_time(gst_buffer.dts),
            format_clock_time(gst_buffer.duration),
            gst_buffer.get_size()))
        latency_log.write(str(time.time()) + "," + str(time.time() - initial_time) + "," +
                          str((time_nanosec - (gst_buffer.pts - 37000000000)) / 1000000.) + "\n")
    return Gst.PadProbeReturn.OK


def str2bool(v):
    return bool(distutils.util.strtobool(v))


def main():
    parser = argparse.ArgumentParser(description='Pravega latency measurement writer.')
    parser.add_argument('--pravega-controller-uri', default='127.0.0.1:9090')
    parser.add_argument('--log_level', type=int, default=logging.INFO, help='10=DEBUG,20=INFO')
    parser.add_argument('--scope', default='test')
    parser.add_argument('--stream', default='latency')
    parser.add_argument("--allow-create-scope", type=str2bool, default=True)
    parser.add_argument("--sleep-seconds", type=float, default=0.0, help="Delay pipeline start by this many seconds")
    args = parser.parse_args()

    logging.basicConfig(level=args.log_level)
    logging.info('args=%s' % str(args))

    # Standard GStreamer initialization.
    Gst.init(None)
    logging.info(Gst.version_string())

    # Create Pipeline element that will form a connection of other elements.
    pipeline_description = (
        "pravegasrc name=source \n" +
        "   ! fakesink name=sink\n"
    )
    logging.info("Creating pipeline: " + pipeline_description)
    pipeline = Gst.parse_launch(pipeline_description)

    # This will cause property changes to be logged as PROPERTY_NOTIFY messages.
    pipeline.add_property_deep_notify_watch(None, True)

    pravegasource = pipeline.get_by_name("source")
    if pravegasource:
        pravegasource.set_property("allow-create-scope", args.allow_create_scope)
        pravegasource.set_property("controller", args.pravega_controller_uri)
        pravegasource.set_property("stream", "%s/%s" % (args.scope, args.stream))

    add_probe(pipeline, "sink", show_metadata_probe, pad_name='sink')

    # Create an event loop and feed GStreamer bus messages to it.
    loop = GLib.MainLoop()
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", bus_call, loop)

    if args.sleep_seconds > 0.0:
        logging.info("Sleeping for %f seconds" % args.sleep_seconds)
        time.sleep(args.sleep_seconds)

    def shutdown_handler(signum, frame):
        logging.info("Shutting down due to received signal %s" % signum)
        loop.quit()

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    # Start play back and listen to events.
    logging.info("Starting pipeline")
    pipeline.set_state(Gst.State.PLAYING)
    try:
        loop.run()
    except:
        logging.error(traceback.format_exc())
        # Cleanup GStreamer elements.
        pipeline.set_state(Gst.State.NULL)
        raise

    pipeline.set_state(Gst.State.NULL)
    latency_log.close()
    logging.info("END")


if __name__ == "__main__":
    main()
