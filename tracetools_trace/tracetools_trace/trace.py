#!/usr/bin/env python3
# Copyright 2019 Robert Bosch GmbH
# Copyright 2021 Christophe Bedard
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Entrypoint/script to setup and start an LTTng tracing session."""

import os
import sys
from typing import List
from typing import Optional

from tracetools_trace.tools import args
from tracetools_trace.tools import lttng
from tracetools_trace.tools import path
from tracetools_trace.tools import print_names_list
from tracetools_trace.tools import signals


def init(
    session_name: str,
    base_path: Optional[str],
    ros_events: List[str],
    kernel_events: List[str],
    context_names: List[str],
    display_list: bool = False,
) -> None:
    """
    Init and start tracing.

    :param session_name: the name of the session
    :param base_path: the path to the directory in which to create the tracing session directory,
    or `None` for default
    :param ros_events: list of ROS events to enable
    :param kernel_events: list of kernel events to enable
    :param context_names: list of context names to enable
    :param display_list: whether to display list(s) of enabled events and context names
    """
    if not lttng.is_lttng_installed():
        sys.exit(2)

    ust_enabled = len(ros_events) > 0
    kernel_enabled = len(kernel_events) > 0
    if ust_enabled:
        print(f'UST tracing enabled ({len(ros_events)} events)')
        if display_list:
            print_names_list(ros_events)
    else:
        print('UST tracing disabled')
    if kernel_enabled:
        print(f'kernel tracing enabled ({len(kernel_events)} events)')
        if display_list:
            print_names_list(kernel_events)
    else:
        print('kernel tracing disabled')
    if len(context_names) > 0:
        print(f'context ({len(context_names)} names)')
        if display_list:
            print_names_list(context_names)

    if not base_path:
        base_path = path.get_tracing_directory()
    full_session_path = os.path.join(base_path, session_name)
    print(f'writing tracing session to: {full_session_path}')

    input('press enter to start...')
    trace_directory = lttng.lttng_init(
        session_name=session_name,
        base_path=base_path,
        ros_events=ros_events,
        kernel_events=kernel_events,
        context_names=context_names,
    )
    # Simple sanity check
    assert trace_directory == full_session_path


def fini(
    session_name: str,
) -> None:
    """
    Stop and finalize tracing.

    :param session_name: the name of the session
    """
    def _run() -> None:
        input('press enter to stop...')

    def _fini() -> None:
        print('stopping & destroying tracing session')
        lttng.lttng_fini(session_name=session_name)

    signals.execute_and_handle_sigint(_run, _fini)


def main():
    params = args.parse_args()

    init(
        params.session_name,
        params.path,
        params.events_ust,
        params.events_kernel,
        params.context_names,
        params.list,
    )
    fini(
        params.session_name,
    )
