# -*- coding: utf-8 -*-

from tele.fields import Command
from tele.tests import tagged

from tele.applets.project.tests.test_project_base import TestProjectCommon


@tagged('-at_install', 'post_install')
class TestTaskDependencies(TestProjectCommon):

    def test_task_dependencies_display_warning_dependency_in_gantt(self):

        Stage = self.env['project.task.type']
        todo_stage = Stage.create({
            'sequence': 1,
            'name': 'TODO',
        })
        fold_stage = Stage.create({
            'sequence': 30,
            'name': 'Done',
            'fold': True,
        })
        close_staged = Stage.create({
            'sequence': 30,
            'name': 'Done',
            'is_closed': True,
        })
        stages = todo_stage + fold_stage + close_staged
        self.project_pigs.write(
            {'type_ids': [Command.link(stage_id) for stage_id in stages.ids]})

        self.task_1.write({'stage_id': todo_stage.id})
        self.assertTrue(self.task_1.display_warning_dependency_in_gantt, 'display_warning_dependency_in_gantt should be True if the task stage is neither closed or fold')
        self.task_1.write({'stage_id': close_staged.id})
        self.assertFalse(self.task_1.display_warning_dependency_in_gantt, 'display_warning_dependency_in_gantt should be False if the task stage is closed')
        self.task_1.write({'stage_id': fold_stage.id})
        self.assertFalse(self.task_1.display_warning_dependency_in_gantt, 'display_warning_dependency_in_gantt should be False if the task stage is fold')
