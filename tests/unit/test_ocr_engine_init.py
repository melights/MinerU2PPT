import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from converter.ocr_merge import PaddleOCREngine


class TestPaddleOCREngineInit(unittest.TestCase):
    def _create_local_model_tree(
        self,
        root: Path,
        variant: str = "server",
        lang: str = "ch",
        include_cls: bool = True,
    ):
        lang_root = root / variant / lang
        required = ["det", "rec"]
        if include_cls:
            required.append("cls")
        for sub in required:
            subdir = lang_root / sub
            subdir.mkdir(parents=True, exist_ok=True)
            (subdir / "inference.pdmodel").write_text("m", encoding="utf-8")
            (subdir / "inference.pdiparams").write_text("p", encoding="utf-8")

    def test_model_root_resolution_prefers_constructor_argument(self):
        with tempfile.TemporaryDirectory() as tempdir:
            explicit_root = Path(tempdir) / "explicit"
            explicit_root.mkdir(parents=True)
            os.environ["MINERU_OCR_MODEL_ROOT"] = str(Path(tempdir) / "env")
            try:
                engine = PaddleOCREngine(model_root=str(explicit_root))
                resolved, source = engine._resolve_model_root()
            finally:
                os.environ.pop("MINERU_OCR_MODEL_ROOT", None)

        self.assertEqual(resolved, explicit_root.resolve())
        self.assertEqual(source, "argument:model_root")

    def test_model_root_resolution_prefers_env_when_argument_missing(self):
        with tempfile.TemporaryDirectory() as tempdir:
            env_root = Path(tempdir) / "env"
            env_root.mkdir(parents=True)
            os.environ["MINERU_OCR_MODEL_ROOT"] = str(env_root)
            try:
                engine = PaddleOCREngine()
                resolved, source = engine._resolve_model_root()
            finally:
                os.environ.pop("MINERU_OCR_MODEL_ROOT", None)

        self.assertEqual(resolved, env_root.resolve())
        self.assertEqual(source, "env:MINERU_OCR_MODEL_ROOT")

    def test_model_root_resolution_prefers_executable_internal_dir_when_present(self):
        with tempfile.TemporaryDirectory() as tempdir:
            exe_path = Path(tempdir) / "app.exe"
            exe_path.write_text("", encoding="utf-8")
            exe_model_root = exe_path.parent / "_internal" / "models" / "paddleocr"
            exe_model_root.mkdir(parents=True)

            with mock.patch.dict(os.environ, {}, clear=False):
                os.environ.pop("MINERU_OCR_MODEL_ROOT", None)
                with mock.patch("converter.ocr_merge.sys.executable", str(exe_path)):
                    engine = PaddleOCREngine()
                    resolved, source = engine._resolve_model_root()

        self.assertIsNone(resolved)
        self.assertEqual(source, "default:download")

    def test_model_root_resolution_prefers_executable_dir_when_present(self):
        with tempfile.TemporaryDirectory() as tempdir:
            exe_path = Path(tempdir) / "app.exe"
            exe_path.write_text("", encoding="utf-8")
            exe_model_root = exe_path.parent / "models" / "paddleocr"
            exe_model_root.mkdir(parents=True)

            with mock.patch.dict(os.environ, {}, clear=False):
                os.environ.pop("MINERU_OCR_MODEL_ROOT", None)
                with mock.patch("converter.ocr_merge.sys.executable", str(exe_path)):
                    engine = PaddleOCREngine()
                    resolved, source = engine._resolve_model_root()

        self.assertIsNone(resolved)
        self.assertEqual(source, "default:download")

    def test_model_root_resolution_falls_back_to_source_dir(self):
        with tempfile.TemporaryDirectory() as tempdir:
            fake_module_file = Path(tempdir) / "repo" / "converter" / "ocr_merge.py"
            fake_module_file.parent.mkdir(parents=True, exist_ok=True)
            fake_module_file.write_text("# placeholder", encoding="utf-8")
            source_root = fake_module_file.parents[1] / "models" / "paddleocr"
            source_root.mkdir(parents=True)

            with mock.patch.dict(os.environ, {}, clear=False):
                os.environ.pop("MINERU_OCR_MODEL_ROOT", None)
                with (
                    mock.patch("converter.ocr_merge.__file__", str(fake_module_file)),
                    mock.patch("converter.ocr_merge.sys.executable", str(Path(tempdir) / "no_app.exe")),
                ):
                    engine = PaddleOCREngine()
                    resolved, source = engine._resolve_model_root()

        self.assertIsNone(resolved)
        self.assertEqual(source, "default:download")

    def test_model_variant_defaults_to_auto(self):
        engine = PaddleOCREngine()
        self.assertEqual(engine.model_variant, "auto")

    def test_invalid_model_variant_raises(self):
        with self.assertRaises(ValueError):
            PaddleOCREngine(model_variant="fast")

    def test_auto_model_variant_uses_lite_when_gpu_unavailable(self):
        with tempfile.TemporaryDirectory() as tempdir:
            model_root = Path(tempdir) / "models" / "paddleocr"
            self._create_local_model_tree(model_root, variant="lite")

            calls = []

            def fake_constructor(**kwargs):
                calls.append(kwargs)
                return object()

            fake_module = SimpleNamespace(PaddleOCR=fake_constructor)
            engine = PaddleOCREngine(model_root=str(model_root), offline_only=False, model_variant="auto")

            with (
                mock.patch.dict("sys.modules", {"paddleocr": fake_module}),
                mock.patch.object(PaddleOCREngine, "_is_gpu_available", return_value=False),
            ):
                engine._ensure_initialized()

        self.assertEqual(engine._active_model_variant, "lite")
        self.assertTrue(any(call.get("text_detection_model_dir") for call in calls))

    def test_server_model_variant_uses_names_when_downloading(self):
        calls = []

        def fake_constructor(**kwargs):
            calls.append(kwargs)
            return object()

        fake_module = SimpleNamespace(PaddleOCR=fake_constructor)
        engine = PaddleOCREngine(offline_only=False, model_variant="server")

        with mock.patch.dict("sys.modules", {"paddleocr": fake_module}):
            engine._ensure_initialized()

        self.assertEqual(engine._active_model_variant, "server")
        self.assertTrue(any(call.get("text_detection_model_name") == "PP-OCRv5_server_det" for call in calls))

    def test_lite_model_variant_uses_names_when_downloading(self):
        calls = []

        def fake_constructor(**kwargs):
            calls.append(kwargs)
            return object()

        fake_module = SimpleNamespace(PaddleOCR=fake_constructor)
        engine = PaddleOCREngine(offline_only=False, model_variant="lite")

        with mock.patch.dict("sys.modules", {"paddleocr": fake_module}):
            engine._ensure_initialized()

        self.assertEqual(engine._active_model_variant, "lite")
        self.assertTrue(any(call.get("text_detection_model_name") == "PP-OCRv5_mobile_det" for call in calls))

    def test_missing_model_path_raises_readable_error(self):
        with tempfile.TemporaryDirectory() as tempdir:
            missing_root = Path(tempdir) / "missing-models"
            fake_module = SimpleNamespace(PaddleOCR=lambda **_kwargs: object())
            engine = PaddleOCREngine(model_root=str(missing_root), offline_only=False, model_variant="server")

            with mock.patch.dict("sys.modules", {"paddleocr": fake_module}):
                with self.assertRaises(RuntimeError) as ctx:
                    engine._ensure_initialized()

        self.assertIn("Local model root not found", str(ctx.exception))
        self.assertIn("models/paddleocr", str(ctx.exception))

    def test_cls_optional_when_angle_disabled(self):
        with tempfile.TemporaryDirectory() as tempdir:
            model_root = Path(tempdir) / "models" / "paddleocr"
            self._create_local_model_tree(model_root, variant="server", include_cls=False)
            fake_module = SimpleNamespace(PaddleOCR=lambda **_kwargs: object())
            engine = PaddleOCREngine(model_root=str(model_root), offline_only=False, use_angle_cls=False, model_variant="server")

            with mock.patch.dict("sys.modules", {"paddleocr": fake_module}):
                engine._ensure_initialized()

            self.assertIsNotNone(engine._ocr)

    def test_cls_required_when_angle_enabled(self):
        with tempfile.TemporaryDirectory() as tempdir:
            model_root = Path(tempdir) / "models" / "paddleocr"
            self._create_local_model_tree(model_root, variant="server", include_cls=False)
            fake_module = SimpleNamespace(PaddleOCR=lambda **_kwargs: object())
            engine = PaddleOCREngine(model_root=str(model_root), offline_only=False, use_angle_cls=True, model_variant="server")

            with mock.patch.dict("sys.modules", {"paddleocr": fake_module}):
                with self.assertRaises(RuntimeError) as ctx:
                    engine._ensure_initialized()

            self.assertIn("Missing model subdirectories", str(ctx.exception))

    def test_auto_mode_falls_back_from_gpu_to_cpu(self):
        with tempfile.TemporaryDirectory() as tempdir:
            model_root = Path(tempdir) / "models" / "paddleocr"
            self._create_local_model_tree(model_root, variant="server")

            calls = []

            class FakeOCR:
                def __init__(self, device):
                    self.device = device

            def fake_constructor(**kwargs):
                calls.append(kwargs.get("device"))
                if kwargs.get("device") == "gpu":
                    raise RuntimeError("gpu failed")
                return FakeOCR("cpu")

            fake_module = SimpleNamespace(PaddleOCR=fake_constructor)
            engine = PaddleOCREngine(device_policy="auto", model_root=str(model_root), offline_only=False, model_variant="server")

            with (
                mock.patch.dict("sys.modules", {"paddleocr": fake_module}),
                mock.patch.object(PaddleOCREngine, "_is_gpu_available", return_value=True),
            ):
                engine._ensure_initialized()

        self.assertIsNotNone(engine._ocr)
        self.assertEqual(engine._ocr.device, "cpu")
        self.assertIn("gpu", calls)
        self.assertIn("cpu", calls)

    def test_gpu_mode_does_not_fallback_to_cpu(self):
        with tempfile.TemporaryDirectory() as tempdir:
            model_root = Path(tempdir) / "models" / "paddleocr"
            self._create_local_model_tree(model_root, variant="server")

            calls = []

            def fake_constructor(**kwargs):
                calls.append(kwargs.get("device"))
                raise RuntimeError("gpu failed")

            fake_module = SimpleNamespace(PaddleOCR=fake_constructor)
            engine = PaddleOCREngine(device_policy="gpu", model_root=str(model_root), offline_only=False, model_variant="server")

            with (
                mock.patch.dict("sys.modules", {"paddleocr": fake_module}),
                mock.patch.object(PaddleOCREngine, "_is_gpu_available", return_value=True),
            ):
                with self.assertRaises(RuntimeError):
                    engine._ensure_initialized()

        self.assertTrue(calls)
        self.assertTrue(all(device == "gpu" for device in calls))

    def test_constructor_attempts_include_tuned_db_params(self):
        with tempfile.TemporaryDirectory() as tempdir:
            model_root = Path(tempdir) / "models" / "paddleocr"
            self._create_local_model_tree(model_root, variant="server")

            engine = PaddleOCREngine(
                device_policy="cpu",
                model_root=str(model_root),
                offline_only=False,
                det_db_thresh=0.35,
                det_db_box_thresh=0.8,
                det_db_unclip_ratio=1.1,
                model_variant="server",
            )

            attempts = list(
                engine._constructor_attempts_for_device(
                    "cpu",
                    engine._build_model_dirs(model_root, "server"),
                    None,
                    {},
                )
            )
            self.assertTrue(attempts)

            has_text_det_variant = any(
                a.get("text_det_thresh") == 0.35
                and a.get("text_det_box_thresh") == 0.8
                and a.get("text_det_unclip_ratio") == 1.1
                for a in attempts
            )
            has_legacy_variant = any(
                a.get("det_db_thresh") == 0.35
                and a.get("det_db_box_thresh") == 0.8
                and a.get("det_db_unclip_ratio") == 1.1
                for a in attempts
            )

            default_engine = PaddleOCREngine(
                device_policy="cpu",
                model_root=str(model_root),
                offline_only=False,
                model_variant="server",
            )
            server_defaults = default_engine._DB_PARAM_DEFAULTS.get("server", {})
            default_attempts = list(
                default_engine._constructor_attempts_for_device(
                    "cpu",
                    default_engine._build_model_dirs(model_root, "server"),
                    None,
                    server_defaults,
                )
            )
            has_default_variant = any(
                a.get("text_det_thresh") == server_defaults.get("det_db_thresh")
                and a.get("text_det_box_thresh") == server_defaults.get("det_db_box_thresh")
                and a.get("text_det_unclip_ratio") == server_defaults.get("det_db_unclip_ratio")
                for a in default_attempts
            )
            has_default_legacy_variant = any(
                a.get("det_db_thresh") == server_defaults.get("det_db_thresh")
                and a.get("det_db_box_thresh") == server_defaults.get("det_db_box_thresh")
                and a.get("det_db_unclip_ratio") == server_defaults.get("det_db_unclip_ratio")
                for a in default_attempts
            )

            lite_defaults = default_engine._DB_PARAM_DEFAULTS.get("lite", {})
            lite_attempts = list(
                default_engine._constructor_attempts_for_device(
                    "cpu",
                    default_engine._build_model_dirs(model_root, "server"),
                    None,
                    lite_defaults,
                )
            )
            has_lite_defaults = any(
                a.get("text_det_thresh") == lite_defaults.get("det_db_thresh")
                and a.get("text_det_box_thresh") == lite_defaults.get("det_db_box_thresh")
                and a.get("text_det_unclip_ratio") == lite_defaults.get("det_db_unclip_ratio")
                for a in lite_attempts
            )
            self.assertTrue(has_text_det_variant)
            self.assertTrue(has_legacy_variant)
            self.assertTrue(has_default_variant)
            self.assertTrue(has_default_legacy_variant)
            self.assertTrue(has_lite_defaults)

    def test_cpu_mode_uses_cpu_only(self):
        with tempfile.TemporaryDirectory() as tempdir:
            model_root = Path(tempdir) / "models" / "paddleocr"
            self._create_local_model_tree(model_root, variant="server")

            calls = []

            class FakeOCR:
                pass

            def fake_constructor(**kwargs):
                calls.append(kwargs.get("device"))
                return FakeOCR()

            fake_module = SimpleNamespace(PaddleOCR=fake_constructor)
            engine = PaddleOCREngine(device_policy="cpu", model_root=str(model_root), offline_only=False, model_variant="server")

            with mock.patch.dict("sys.modules", {"paddleocr": fake_module}):
                engine._ensure_initialized()

        self.assertIsNotNone(engine._ocr)
        self.assertTrue(calls)
        self.assertTrue(all(device == "cpu" for device in calls))


if __name__ == "__main__":
    unittest.main()
