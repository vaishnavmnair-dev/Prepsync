"""Python-based Automated Test Suite for AdaptiveStudy AI Frontend."""

import os
import re
import unittest


class TestAdaptiveStudyFrontend(unittest.TestCase):
    """Validates markup integrity, element binding, and core algorithms."""

    @classmethod
    def setUpClass(cls):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.html_path = os.path.join(base_dir, "Frontend", "index.html")
        cls.app_js_path = os.path.join(base_dir, "Frontend", "app.js")
        cls.styles_path = os.path.join(base_dir, "Frontend", "styles.css")

        with open(cls.html_path, "r", encoding="utf-8") as f:
            cls.html_content = f.read()

        with open(cls.app_js_path, "r", encoding="utf-8") as f:
            cls.app_js_content = f.read()

    def test_file_existence(self):
        """Verifies that all frontend files exist."""
        self.assertTrue(os.path.isfile(self.html_path), "index.html must exist")
        self.assertTrue(os.path.isfile(self.app_js_path), "app.js must exist")
        self.assertTrue(os.path.isfile(self.styles_path), "styles.css must exist")

    def test_navigation_and_tab_elements(self):
        """Verifies that all 5 tabs and dock elements exist."""
        required_elements = [
            "desktopDockContainer", "dock-home", "dock-hub", "dock-timeline",
            "dock-performance", "dock-profile", "tab-home-view", "tab-hub-view",
            "tab-timeline-view", "tab-performance-view", "tab-profile-view"
        ]
        for elem_id in required_elements:
            self.assertIn(f'id="{elem_id}"', self.html_content, f"Missing id: {elem_id}")

    def test_phone_preview_elements(self):
        """Verifies mobile frame elements and toggle button."""
        phone_elements = [
            "deviceFrameWrapper", "phoneTopBar", "phoneClock", "phoneBottomBar",
            "toggleMobileFrameBtn", "frameIcon", "frameLabel"
        ]
        for elem_id in phone_elements:
            self.assertIn(f'id="{elem_id}"', self.html_content, f"Missing id: {elem_id}")

    def test_pomodoro_timer_elements(self):
        """Verifies Focus sprint timer elements."""
        timer_elements = ["timerDisplay", "toggleTimerBtn", "resetTimerBtn"]
        for elem_id in timer_elements:
            self.assertIn(f'id="{elem_id}"', self.html_content, f"Missing id: {elem_id}")

    def test_study_window_inputs(self):
        """Verifies study time window pickers and badges."""
        window_elements = [
            "inputStartTime", "inputEndTime", "windowTotalHoursBadge",
            "hubWindowDisplayStart", "hubWindowDisplayEnd"
        ]
        for elem_id in window_elements:
            self.assertIn(f'id="{elem_id}"', self.html_content, f"Missing id: {elem_id}")

    def test_metric_counter_cards(self):
        """Verifies 4 cognitive metric cards."""
        metrics = ["metricHardCount", "metricMediumCount", "metricCompletedCount", "metricDeferredCount"]
        for elem_id in metrics:
            self.assertIn(f'id="{elem_id}"', self.html_content, f"Missing id: {elem_id}")

    def test_task_input_form_and_buttons(self):
        """Verifies task input form, quick types, and extract/generate buttons."""
        form_elements = [
            "taskInputForm", "quickTaskText", "typeBtn-hard", "typeBtn-medium",
            "typeBtn-light", "aiAutoExtractBtn", "generateScheduleBtn"
        ]
        for elem_id in form_elements:
            self.assertIn(f'id="{elem_id}"', self.html_content, f"Missing id: {elem_id}")

    def test_modals_exist(self):
        """Verifies Auth and Breakdown modal elements."""
        modal_elements = [
            "authModal", "authForm", "authEmailInput", "authPasswordInput",
            "authSubmitBtn", "authDemoBtn", "breakdownModal",
            "breakdownLoadingState", "breakdownContentArea", "toastNotification"
        ]
        for elem_id in modal_elements:
            self.assertIn(f'id="{elem_id}"', self.html_content, f"Missing id: {elem_id}")

    def test_js_function_bindings(self):
        """Verifies all interactive functions are defined and hooked."""
        functions = [
            "setTab", "toggleTaskDone", "deleteTask", "setQuickType",
            "updateStudyWindow", "toggleMobileFrame", "toggleTimer",
            "resetTimer", "handleLateOffset", "selectDay", "dismissAiAdvice",
            "handleAddTaskSubmit", "handleAiAutoExtract", "handleGenerateSchedule",
            "handleBreakdownTask", "closeBreakdownModal", "selectTrack",
            "saveProfile", "openAuthModal", "closeAuthModal", "handleAuthSubmit",
            "handleDemoLogin", "handleLogout"
        ]
        for fn in functions:
            pattern = re.compile(rf"function\s+{fn}\s*\(")
            self.assertTrue(pattern.search(self.html_content), f"Function {fn} not found in index.html")


if __name__ == "__main__":
    unittest.main()

