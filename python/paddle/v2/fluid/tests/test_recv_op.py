#   Copyright (c) 2018 PaddlePaddle Authors. All Rights Reserve.
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

import unittest

import paddle.v2.fluid as fluid
import paddle.v2.fluid.layers as layers
import numpy
import threading


class TestRecvOp(unittest.TestCase):
    def test_send(self):
        # Run init_serv in a thread
        place = fluid.CPUPlace()
        t = threading.Thread(target=self.init_serv, args=(place, ))
        t.start()
        self.init_client(place)
        t.join()

    def init_serv(self, place):
        main = fluid.Program()
        with fluid.program_guard(main):
            x = layers.data(shape=[32, 32], dtype='float32', name='X')
            i = fluid.initializer.Constant(value=1.0)
            y = i(x, main.global_block())
            serv = layers.ListenAndServ("127.0.0.1:6174")
            with serv.do():
                layers.scale(input=y, scale=10.0)
        exe = fluid.Executor(place)
        exe.run(main)

    def init_client(self, place):
        main = fluid.Program()
        with fluid.program_guard(main):
            x = layers.data(shape=[32, 32], dtype='float32', name='X')
            i = fluid.initializer.Constant(value=1.0)
            i(x, main.global_block())
            layers.Send("127.0.0.1:6174", [x], [x])
        exe = fluid.Executor(place)
        exe.run(main)


if __name__ == "__main__":
    unittest.main()
