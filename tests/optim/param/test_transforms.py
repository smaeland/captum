#!/usr/bin/env python3
import unittest
from typing import List

import numpy as np
import torch
import torch.nn.functional as F

from captum.optim._param.image import transform
from tests.helpers.basic import (
    BaseTest,
    assertArraysAlmostEqual,
    assertTensorAlmostEqual,
)
from tests.optim.helpers import numpy_transforms


class TestRandSelect(BaseTest):
    def test_rand_select(self) -> None:
        a = (1, 2, 3, 4, 5)
        b = torch.Tensor([0.1, -5, 56.7, 99.0])

        self.assertIn(transform.rand_select(a), a)
        self.assertIn(transform.rand_select(b), b)


class TestRandomScale(BaseTest):
    def test_random_scale(self) -> None:
        scale_module = transform.RandomScale(scale=(1, 0.975, 1.025, 0.95, 1.05))
        test_tensor = torch.ones(1, 3, 3, 3)

        # Test rescaling
        assertTensorAlmostEqual(
            self,
            scale_module.scale_tensor(test_tensor, 0.5),
            torch.ones(3, 1).repeat(3, 1, 3).unsqueeze(0),
            0,
        )

        assertTensorAlmostEqual(
            self,
            scale_module.scale_tensor(test_tensor, 1.5),
            torch.tensor(
                [
                    [0.2500, 0.5000, 0.2500],
                    [0.5000, 1.0000, 0.5000],
                    [0.2500, 0.5000, 0.2500],
                ]
            )
            .repeat(3, 1, 1)
            .unsqueeze(0),
            0,
        )

    def test_random_scale_matrix(self) -> None:
        scale_module = transform.RandomScale(scale=(1, 0.975, 1.025, 0.95, 1.05))
        test_tensor = torch.ones(1, 3, 3, 3)
        # Test scale matrices

        assertTensorAlmostEqual(
            self,
            scale_module.get_scale_mat(0.5, test_tensor.device, test_tensor.dtype),
            torch.tensor([[0.5000, 0.0000, 0.0000], [0.0000, 0.5000, 0.0000]]),
            0,
        )

        assertTensorAlmostEqual(
            self,
            scale_module.get_scale_mat(1.24, test_tensor.device, test_tensor.dtype),
            torch.tensor([[1.2400, 0.0000, 0.0000], [0.0000, 1.2400, 0.0000]]),
            0,
        )


class TestRandomSpatialJitter(BaseTest):
    def test_random_spatial_jitter_hw(self) -> None:
        translate_vals = [4, 4]
        t_val = 3

        spatialjitter = transform.RandomSpatialJitter(t_val)
        test_input = torch.eye(4, 4).repeat(3, 1, 1).unsqueeze(0)
        jittered_tensor = spatialjitter.translate_tensor(
            test_input, torch.tensor(translate_vals)
        ).squeeze(0)

        spatial_mod_np = numpy_transforms.RandomSpatialJitter(t_val)
        jittered_array = spatial_mod_np.translate_array(np.eye(4, 4), translate_vals)

        assertArraysAlmostEqual(jittered_tensor[0].numpy(), jittered_array, 0)
        assertArraysAlmostEqual(jittered_tensor[1].numpy(), jittered_array, 0)
        assertArraysAlmostEqual(jittered_tensor[2].numpy(), jittered_array, 0)

    def test_random_spatial_jitter_w(self) -> None:
        translate_vals = [0, 3]
        t_val = 3

        spatialjitter = transform.RandomSpatialJitter(t_val)
        test_input = torch.eye(4, 4).repeat(3, 1, 1).unsqueeze(0)
        jittered_tensor = spatialjitter.translate_tensor(
            test_input, torch.tensor(translate_vals)
        ).squeeze(0)

        spatial_mod_np = numpy_transforms.RandomSpatialJitter(t_val)
        jittered_array = spatial_mod_np.translate_array(np.eye(4, 4), translate_vals)

        assertArraysAlmostEqual(jittered_tensor[0].numpy(), jittered_array, 0)
        assertArraysAlmostEqual(jittered_tensor[1].numpy(), jittered_array, 0)
        assertArraysAlmostEqual(jittered_tensor[2].numpy(), jittered_array, 0)

    def test_random_spatial_jitter_h(self) -> None:
        translate_vals = [3, 0]
        t_val = 3

        spatialjitter = transform.RandomSpatialJitter(t_val)
        test_input = torch.eye(4, 4).repeat(3, 1, 1).unsqueeze(0)
        jittered_tensor = spatialjitter.translate_tensor(
            test_input, torch.tensor(translate_vals)
        ).squeeze(0)

        spatial_mod_np = numpy_transforms.RandomSpatialJitter(t_val)
        jittered_array = spatial_mod_np.translate_array(np.eye(4, 4), translate_vals)

        assertArraysAlmostEqual(jittered_tensor[0].numpy(), jittered_array, 0)
        assertArraysAlmostEqual(jittered_tensor[1].numpy(), jittered_array, 0)
        assertArraysAlmostEqual(jittered_tensor[2].numpy(), jittered_array, 0)


class TestCenterCrop(BaseTest):
    def test_center_crop_one_number(self) -> None:
        pad = (1, 1, 1, 1)
        test_tensor = (
            F.pad(F.pad(torch.ones(2, 2), pad=pad), pad=pad, value=1)
            .repeat(3, 1, 1)
            .unsqueeze(0)
        )
        test_array = np.pad(
            np.pad(np.ones((2, 2)), pad_width=1), pad_width=1, constant_values=(1)
        )[None, None, :]

        crop_vals = 3

        crop_tensor = transform.CenterCrop(size=crop_vals)
        cropped_tensor = crop_tensor(test_tensor)

        crop_mod_np = numpy_transforms.CenterCrop(crop_vals)
        cropped_array = crop_mod_np.crop(test_array)

        assertArraysAlmostEqual(cropped_tensor.numpy(), cropped_array, 0)

    def test_center_crop_two_numbers(self) -> None:
        pad = (1, 1, 1, 1)
        test_tensor = (
            F.pad(F.pad(torch.ones(2, 2), pad=pad), pad=pad, value=1)
            .repeat(3, 1, 1)
            .unsqueeze(0)
        )
        test_array = np.pad(
            np.pad(np.ones((2, 2)), pad_width=1), pad_width=1, constant_values=(1)
        )[None, None, :]

        crop_vals = (4, 0)

        crop_tensor = transform.CenterCrop(size=crop_vals)
        cropped_tensor = crop_tensor(test_tensor)

        crop_mod_np = numpy_transforms.CenterCrop(crop_vals)
        cropped_array = crop_mod_np.crop(test_array)

        assertArraysAlmostEqual(cropped_tensor.numpy(), cropped_array, 0)


class TestCenterCropShape(BaseTest):
    def test_center_crop_shape_tuple(self) -> None:
        x = torch.ones(32, 16, 28, 28)

        x_out = transform.center_crop_shape(x, (5, 5))

        self.assertEqual(list(x_out.shape), [32, 16, 5, 5])

    def test_center_crop_shape_int(self) -> None:
        x = torch.ones(32, 16, 28, 28)

        x_out = transform.center_crop_shape(x, 5)

        self.assertEqual(list(x_out.shape), [32, 16, 5, 5])


class TestBlendAlpha(BaseTest):
    def test_blend_alpha(self) -> None:
        rgb_tensor = torch.ones(3, 3, 3)
        alpha_tensor = ((torch.eye(3, 3) + torch.eye(3, 3).flip(1)) / 2).repeat(1, 1, 1)
        test_tensor = torch.cat([rgb_tensor, alpha_tensor]).unsqueeze(0)

        background_tensor = torch.ones_like(rgb_tensor) * 5
        blend_alpha = transform.BlendAlpha(background=background_tensor)
        blended_tensor = blend_alpha(test_tensor)

        rgb_array = np.ones((3, 3, 3))
        alpha_array = (np.add(np.eye(3, 3), np.flip(np.eye(3, 3), 1)) / 2)[None, :]
        test_array = np.concatenate([rgb_array, alpha_array])[None, :]

        background_array = np.ones(rgb_array.shape) * 5
        blend_alpha_np = numpy_transforms.BlendAlpha(background=background_array)
        blended_array = blend_alpha_np.blend_alpha(test_array)

        assertArraysAlmostEqual(blended_tensor.numpy(), blended_array, 0)


class TestIgnoreAlpha(BaseTest):
    def test_ignore_alpha(self) -> None:
        ignore_alpha = transform.IgnoreAlpha()
        test_input = torch.ones(1, 4, 3, 3)
        rgb_tensor = ignore_alpha(test_input)
        assert rgb_tensor.size(1) == 3


class TestToRGB(BaseTest):
    def test_to_rgb_i1i2i3(self) -> None:
        to_rgb = transform.ToRGB(transform_name="i1i2i3")
        to_rgb_np = numpy_transforms.ToRGB(transform_name="i1i2i3")
        assertArraysAlmostEqual(to_rgb.transform.numpy(), to_rgb_np.transform)

    def test_to_rgb_klt(self) -> None:
        to_rgb = transform.ToRGB(transform_name="klt")
        to_rgb_np = numpy_transforms.ToRGB(transform_name="klt")
        assertArraysAlmostEqual(to_rgb.transform.numpy(), to_rgb_np.transform)

    def test_to_rgb_klt_forward(self) -> None:
        if torch.__version__ == "1.2.0":
            raise unittest.SkipTest(
                "Skipping ToRGB forward due to insufficient Torch version."
            )
        to_rgb = transform.ToRGB(transform_name="klt")
        test_tensor = torch.ones(3, 4, 4).unsqueeze(0).refine_names("B", "C", "H", "W")
        rgb_tensor = to_rgb(test_tensor)

        to_rgb_np = numpy_transforms.ToRGB(transform_name="klt")
        test_array = np.ones((1, 3, 4, 4))
        rgb_array = to_rgb_np.to_rgb(test_array)

        assertArraysAlmostEqual(rgb_tensor.numpy(), rgb_array)

        inverse_tensor = to_rgb(rgb_tensor.clone(), inverse=True)
        inverse_array = to_rgb_np.to_rgb(rgb_array, inverse=True)

        assertArraysAlmostEqual(inverse_tensor.numpy(), inverse_array)

    def test_to_rgb_alpha_klt_forward(self) -> None:
        if torch.__version__ == "1.2.0":
            raise unittest.SkipTest(
                "Skipping ToRGB with Alpha forward due to insufficient Torch version."
            )
        to_rgb = transform.ToRGB(transform_name="klt")
        test_tensor = torch.ones(4, 4, 4).unsqueeze(0).refine_names("B", "C", "H", "W")
        rgb_tensor = to_rgb(test_tensor)

        to_rgb_np = numpy_transforms.ToRGB(transform_name="klt")
        test_array = np.ones((1, 4, 4, 4))
        rgb_array = to_rgb_np.to_rgb(test_array)

        assertArraysAlmostEqual(rgb_tensor.numpy(), rgb_array)

        inverse_tensor = to_rgb(rgb_tensor, inverse=True)
        inverse_array = to_rgb_np.to_rgb(rgb_array, inverse=True)

        assertArraysAlmostEqual(inverse_tensor.numpy(), inverse_array)

    def test_to_rgb_i1i2i3_forward(self) -> None:
        if torch.__version__ == "1.2.0":
            raise unittest.SkipTest(
                "Skipping ToRGB forward due to insufficient Torch version."
            )
        to_rgb = transform.ToRGB(transform_name="i1i2i3")
        test_tensor = torch.ones(3, 4, 4).unsqueeze(0).refine_names("B", "C", "H", "W")
        rgb_tensor = to_rgb(test_tensor)

        to_rgb_np = numpy_transforms.ToRGB(transform_name="i1i2i3")
        test_array = np.ones((1, 3, 4, 4))
        rgb_array = to_rgb_np.to_rgb(test_array)

        assertArraysAlmostEqual(rgb_tensor.numpy(), rgb_array)

        inverse_tensor = to_rgb(rgb_tensor.clone(), inverse=True)
        inverse_array = to_rgb_np.to_rgb(rgb_array, inverse=True)

        assertArraysAlmostEqual(inverse_tensor.numpy(), inverse_array)

    def test_to_rgb_alpha_i1i2i3_forward(self) -> None:
        if torch.__version__ == "1.2.0":
            raise unittest.SkipTest(
                "Skipping ToRGB with Alpha forward due to insufficient Torch version."
            )
        to_rgb = transform.ToRGB(transform_name="i1i2i3")
        test_tensor = torch.ones(4, 4, 4).unsqueeze(0).refine_names("B", "C", "H", "W")
        rgb_tensor = to_rgb(test_tensor)

        to_rgb_np = numpy_transforms.ToRGB(transform_name="i1i2i3")
        test_array = np.ones((1, 4, 4, 4))
        rgb_array = to_rgb_np.to_rgb(test_array)

        assertArraysAlmostEqual(rgb_tensor.numpy(), rgb_array)

        inverse_tensor = to_rgb(rgb_tensor, inverse=True)
        inverse_array = to_rgb_np.to_rgb(rgb_array, inverse=True)

        assertArraysAlmostEqual(inverse_tensor.numpy(), inverse_array)


class TestGaussianSmoothing(BaseTest):
    def test_gaussian_smoothing_1d(self) -> None:
        channels = 6
        kernel_size = 3
        sigma = 2.0
        dim = 1
        smoothening_module = transform.GaussianSmoothing(
            channels, kernel_size, sigma, dim
        )

        test_tensor = torch.tensor([1.0, 5.0]).repeat(6, 2).unsqueeze(0)

        diff_tensor = smoothening_module(test_tensor) - torch.tensor(
            [2.4467, 3.5533]
        ).repeat(6, 1).unsqueeze(0)
        self.assertLessEqual(diff_tensor.max().item(), 4.268e-05)
        self.assertGreaterEqual(diff_tensor.min().item(), -4.197e-05)

    def test_gaussian_smoothing_2d(self) -> None:
        channels = 3
        kernel_size = 3
        sigma = 2.0
        dim = 2
        smoothening_module = transform.GaussianSmoothing(
            channels, kernel_size, sigma, dim
        )

        test_tensor = torch.tensor([1.0, 5.0]).repeat(3, 6, 3).unsqueeze(0)

        diff_tensor = smoothening_module(test_tensor) - torch.tensor(
            [2.4467, 3.5533]
        ).repeat(3, 4, 2).unsqueeze(0)
        self.assertLessEqual(diff_tensor.max().item(), 4.5539e-05)
        self.assertGreaterEqual(diff_tensor.min().item(), -4.5539e-05)

    def test_gaussian_smoothing_3d(self) -> None:
        channels = 4
        kernel_size = 3
        sigma = 1.021
        dim = 3
        smoothening_module = transform.GaussianSmoothing(
            channels, kernel_size, sigma, dim
        )

        test_tensor = torch.tensor([1.0, 5.0, 1.0]).repeat(4, 6, 6, 2).unsqueeze(0)

        diff_tensor = smoothening_module(test_tensor) - torch.tensor(
            [2.7873, 2.1063, 2.1063, 2.7873]
        ).repeat(4, 4, 4, 1).unsqueeze(0)
        t_max = diff_tensor.max().item()
        t_min = diff_tensor.min().item()
        self.assertLessEqual(t_max, 4.8162e-05)
        self.assertGreaterEqual(t_min, 3.3377e-06)


class TestScaleInputRange(BaseTest):
    def test_scale_input_range(self) -> None:
        x = torch.ones(1, 3, 4, 4)
        scale_input = transform.ScaleInputRange(255)
        output_tensor = scale_input(x)
        self.assertEqual(output_tensor.mean(), 255.0)


class TestRGBToBGR(BaseTest):
    def test_rgb_to_bgr(self) -> None:
        x = torch.randn(1, 3, 224, 224)
        rgb_to_bgr = transform.RGBToBGR()
        output_tensor = rgb_to_bgr(x)
        expected_x = x[:, [2, 1, 0]]
        assertTensorAlmostEqual(self, output_tensor, expected_x)


class TestSymmetricPadding(BaseTest):
    def test_symmetric_padding(self) -> None:
        b = 2
        c = 3
        x = torch.arange(0, b * c * 4 * 4).view(b, c, 4, 4).float()
        offset_pad = [[3, 3], [4, 4], [2, 2], [5, 5]]

        x_pt = torch.nn.Parameter(x)
        x_out = transform.SymmetricPadding.apply(x_pt, offset_pad)
        x_out_np = torch.as_tensor(
            np.pad(x.detach().numpy(), pad_width=offset_pad, mode="symmetric")
        )
        assertTensorAlmostEqual(self, x_out, x_out_np)

    def test_symmetric_padding_backward(self) -> None:
        b = 2
        c = 3
        x = torch.arange(0, b * c * 4 * 4).view(b, c, 4, 4).float()
        offset_pad = [[3, 3], [4, 4], [2, 2], [5, 5]]

        x_pt = torch.nn.Parameter(x) * 1

        t_grad_input, t_grad_output = [], []

        def check_grad(self, grad_input, grad_output):
            t_grad_input.append(grad_input[0].clone().detach())
            t_grad_output.append(grad_output[0].clone().detach())

        class SymmetricPaddingLayer(torch.nn.Module):
            def forward(
                self, x: torch.Tensor, padding: List[List[int]]
            ) -> torch.Tensor:
                return transform.SymmetricPadding.apply(x_pt, padding)

        sym_pad = SymmetricPaddingLayer()
        sym_pad.register_backward_hook(check_grad)
        x_out = sym_pad(x_pt, offset_pad)
        (x_out.sum() * 1).backward()

        self.assertEqual(x.shape, t_grad_input[0].shape)

        x_out_np = torch.as_tensor(
            np.pad(x.detach().numpy(), pad_width=offset_pad, mode="symmetric")
        )
        aelf.assertEqual(x_out_np.shape, t_grad_output[0].shape)


class TestNChannelsToRGB(BaseTest):
    def test_nchannels_to_rgb_collapse(self) -> None:
        test_input = torch.randn(1, 6, 224, 224)
        nchannels_to_rgb = transform.NChannelsToRGB()
        test_output = nchannels_to_rgb(test_input)
        self.assertEqual(list(test_output.size()), [1, 3, 224, 224])

    def test_nchannels_to_rgb_increase(self) -> None:
        test_input = torch.randn(1, 2, 224, 224)
        nchannels_to_rgb = transform.NChannelsToRGB()
        test_output = nchannels_to_rgb(test_input)
        self.assertEqual(list(test_output.size()), [1, 3, 224, 224])


if __name__ == "__main__":
    unittest.main()
