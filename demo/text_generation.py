"""
Copyright 2018 Lambda Labs. All Rights Reserved.
Licensed under
==========================================================================
"""
import sys
import os
import importlib


def main():

  sys.path.append('.')

  from source.tool import downloader
  from source.tool import tuner
  from source.tool import config_parser

  parser = config_parser.default_parser()

  config = parser.parse_args()

  config = config_parser.prepare(config)

  # Generate config
  runner_config, callback_config, inputter_config, modeler_config = \
      config_parser.default_config(config)

  # Download data if necessary
  downloader.check_and_download(inputter_config)

  if config.mode == "tune":

    inputter_module = importlib.import_module(
      "source.inputter.text_generation_txt_inputter")
    modeler_module = importlib.import_module(
      "source.modeler.text_generation_modeler")
    runner_module = importlib.import_module(
      "source.runner.parameter_server_runner")

    tuner.tune(config,
               runner_config,
               callback_config,
               inputter_config,
               modeler_config,
               inputter_module,
               modeler_module,
               runner_module)
  else:

    """
    An application owns a runner.
    Runner: Distributes a job across devices, schedules the excution.
            It owns an inputter and a modeler.
    Inputter: Handles the data pipeline.
              It (optionally) owns a data augmenter.
    Modeler: Creates functions for network, loss, optimization and evaluation.
             It owns a network and a list of callbacks as inputs.

    """

    augmenter = (None if not config.augmenter else
                 importlib.import_module(
                  "source.augmenter." + config.augmenter))

    net = importlib.import_module("source.network." + config.network)

    callbacks = []
    for name in config.callbacks:
      callback = importlib.import_module(
        "source.callback." + name).build(callback_config)
      callbacks.append(callback)

    inputter = importlib.import_module(
      "source.inputter.text_generation_txt_inputter").build(
      inputter_config, augmenter)

    modeler = importlib.import_module(
      "source.modeler.text_generation_modeler").build(
      modeler_config, net)

    runner = importlib.import_module(
      "source.runner.parameter_server_runner").build(
      runner_config, inputter, modeler, callbacks)

    # Run application
    runner.run()


if __name__ == "__main__":
  main()
