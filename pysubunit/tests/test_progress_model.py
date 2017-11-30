# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from pysubunit import progress_model
from pysubunit.tests import base


class TestProgressModel(base.TestCase):

    def assertProgressSummary(self, pos, total, progress):
        """Assert that a progress model has reached a particular point."""
        self.assertEqual(pos, progress.pos())
        self.assertEqual(total, progress.width())

    def test_new_progress_0_0(self):
        progress = progress_model.ProgressModel()
        self.assertProgressSummary(0, 0, progress)

    def test_advance_0_0(self):
        progress = progress_model.ProgressModel()
        progress.advance()
        self.assertProgressSummary(1, 0, progress)

    def test_advance_1_0(self):
        progress = progress_model.ProgressModel()
        progress.advance()
        self.assertProgressSummary(1, 0, progress)

    def test_set_width_absolute(self):
        progress = progress_model.ProgressModel()
        progress.set_width(10)
        self.assertProgressSummary(0, 10, progress)

    def test_set_width_absolute_preserves_pos(self):
        progress = progress_model.ProgressModel()
        progress.advance()
        progress.set_width(2)
        self.assertProgressSummary(1, 2, progress)

    def test_adjust_width(self):
        progress = progress_model.ProgressModel()
        progress.adjust_width(10)
        self.assertProgressSummary(0, 10, progress)
        progress.adjust_width(-10)
        self.assertProgressSummary(0, 0, progress)

    def test_adjust_width_preserves_pos(self):
        progress = progress_model.ProgressModel()
        progress.advance()
        progress.adjust_width(10)
        self.assertProgressSummary(1, 10, progress)
        progress.adjust_width(-10)
        self.assertProgressSummary(1, 0, progress)

    def test_push_preserves_progress(self):
        progress = progress_model.ProgressModel()
        progress.adjust_width(3)
        progress.advance()
        progress.push()
        self.assertProgressSummary(1, 3, progress)

    def test_advance_advances_substack(self):
        progress = progress_model.ProgressModel()
        progress.adjust_width(3)
        progress.advance()
        progress.push()
        progress.adjust_width(1)
        progress.advance()
        self.assertProgressSummary(2, 3, progress)

    def test_adjust_width_adjusts_substack(self):
        progress = progress_model.ProgressModel()
        progress.adjust_width(3)
        progress.advance()
        progress.push()
        progress.adjust_width(2)
        progress.advance()
        self.assertProgressSummary(3, 6, progress)

    def test_set_width_adjusts_substack(self):
        progress = progress_model.ProgressModel()
        progress.adjust_width(3)
        progress.advance()
        progress.push()
        progress.set_width(2)
        progress.advance()
        self.assertProgressSummary(3, 6, progress)

    def test_pop_restores_progress(self):
        progress = progress_model.ProgressModel()
        progress.adjust_width(3)
        progress.advance()
        progress.push()
        progress.adjust_width(1)
        progress.advance()
        progress.pop()
        self.assertProgressSummary(1, 3, progress)
