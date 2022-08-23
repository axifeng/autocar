// Copyright (c) 2019 PaddlePaddle Authors. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include "pybind.h"
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include <cstring>
#include <iostream>
#include <map>
#include <memory>
#include <string>
#include <unordered_set>
#include <utility>
#include <vector>

#include "paddle_api.h"
// #include "paddle_use_kernels.h"
// #include "paddle_use_ops.h"

namespace paddle {
namespace lite {
namespace pybind {

using TargetType = lite_api::TargetType;
using PrecisionType = lite_api::PrecisionType;
using DataLayoutType = lite_api::DataLayoutType;
using PowerMode = lite_api::PowerMode;
using ActivationType = lite_api::ActivationType;

using Place = lite_api::Place;
using Tensor = lite_api::Tensor;
using ConfigBase = lite_api::ConfigBase;
using CxxConfig = lite_api::CxxConfig;
using PaddlePredictor = lite_api::PaddlePredictor;

template <typename T>
std::vector<T> tuple_to_vector(const py::tuple& t) {
  std::vector<T> v(t.size());
  for (int j = 0; j < t.size();j++) {
    v[j] = t[j].cast<T>();
  };
  return v;
}

template <typename T>
py::tuple vector_to_tuple(std::vector<T>& v) {
  py::tuple t(v.size());
  for (size_t i = 0; i < v.size(); i++) {
    t[i] = v[i];
  }
  return t;
}

class PredictorWrapper {
  public:
  std::shared_ptr<PaddlePredictor> p_;
  void run(){
    p_->Run();
  };

  std::unique_ptr<Tensor> getInput(int index) {
    return p_->GetInput(index);
  }

  std::unique_ptr<const Tensor> getOutput(int index) {
    return p_->GetOutput(index);
  }
};

void py_bind_enums(py::module &m) {
  py::enum_<TargetType>(m, "TargetType", py::arithmetic())
    .value("kUnk", TargetType::kUnk  )
    .value("kHost", TargetType::kHost  )
    .value("kX86", TargetType::kX86  )
    .value("kCUDA", TargetType::kCUDA  )
    .value("kARM", TargetType::kARM)
    .value("kOpenCL", TargetType::kOpenCL  )
    .value("kFPGA", TargetType::kFPGA  )
    .value("kNPU", TargetType::kNPU)
    .value("kXPU", TargetType::kXPU  )
    .value("kAny", TargetType::kAny  );

  py::enum_<PrecisionType>(m, "PrecisionType", py::arithmetic())
    .value("kUnk", PrecisionType::kUnk)
    .value("kFloat", PrecisionType::kFloat)
    .value("kInt8", PrecisionType::kInt8  )
    .value("kInt32", PrecisionType::kInt32  )
    .value("kAny", PrecisionType::kAny)
    .value("kFP16", PrecisionType::kFP16  )
    .value("kBool", PrecisionType::kBool  )
    .value("kInt64", PrecisionType::kInt64)
    .value("kInt16", PrecisionType::kInt16  );

  py::enum_<DataLayoutType>(m, "DataLayoutType", py::arithmetic())
    .value("kUnk", DataLayoutType::kUnk)
    .value("kNCHW", DataLayoutType::kNCHW)
    .value("kNHWC", DataLayoutType::kNHWC  )
    .value("kImageDefault", DataLayoutType::kImageDefault  )
    .value("kImageFolder", DataLayoutType::kImageFolder)
    .value("kImageNW", DataLayoutType::kImageNW  )
    .value("kAny", DataLayoutType::kAny  );

  py::enum_<PowerMode>(m, "PowerMode", py::arithmetic())
    .value("HIGH", PowerMode::LITE_POWER_HIGH)
    .value("LOW", PowerMode::LITE_POWER_LOW)
    .value("FULL",   PowerMode::LITE_POWER_FULL  )
    .value("NO_BIND",   PowerMode::LITE_POWER_NO_BIND  )
    .value("RAND_HIGH", PowerMode::LITE_POWER_RAND_HIGH)
    .value("RAND_LOW",   PowerMode::LITE_POWER_RAND_LOW  );

  py::enum_<ActivationType>(m, "ActivationType", py::arithmetic())
    .value("kIndentity", ActivationType::kIndentity  )
    .value("kRelu", ActivationType::kRelu  )
    .value("kRelu6",   ActivationType::kRelu6  )
    .value("kPRelu",   ActivationType::kPRelu  )
    .value("kLeakyRelu", ActivationType::kLeakyRelu)
    .value("kSigmoid",   ActivationType::kSigmoid  )
    .value("kTanh", ActivationType::kTanh)
    .value("kSwish",   ActivationType::kSwish  );

  py::class_<Place>(m, "Place")
    .def(py::init())
    .def(py::init<TargetType&,PrecisionType&, DataLayoutType&>())
    .def(py::init<TargetType&,PrecisionType&>())
    .def_readwrite("target",      &Place::target)
    .def_readwrite("precision",         &Place::precision)
    .def_readwrite("layout",      &Place::layout)
    .def_readwrite("device",      &Place::device);
}

template<typename T>
void copy_data(const Tensor &pt, py::buffer_info& buf) {
  auto strides = buf.strides;
  if (strides[0] == buf.size * sizeof(T)) {
    memcpy(pt.mutable_data<T>(), buf.ptr, buf.size * sizeof(T));
  } else {
    std::cout << "not a dense numpy array\n";
    exit(-1);
  }
}

void py_bind_tensor(py::module& m) {
  auto lod_getter = [](const Tensor &tensor) -> py::tuple {
    auto lod = tensor.lod();
    py::tuple o(lod.size());
    for (size_t i = 0; i < lod.size(); i++) {
      auto inner = lod[i];
      o[i] = vector_to_tuple<uint64_t>(inner);
    }
    return o;
  };

  auto lod_setter = [](Tensor &tensor, const py::tuple& t) -> void {
    std::vector<std::vector<uint64_t>> lod(t.size());
    for (int i = 0; i < t.size(); i++) {
      auto inner = t[i].cast<py::tuple>();
      lod[i] = tuple_to_vector<uint64_t>(inner);
    };
  };

  py::class_<Tensor>(m, "Tensor", py::buffer_protocol())
    .def("shape", [](const Tensor &pt) -> py::tuple {
      auto shape = pt.shape();
      return vector_to_tuple(shape);
    })
    .def("target", [](const Tensor &pt) -> TargetType {
      return pt.target();
    })
    .def("precision",[](const Tensor &pt) -> PrecisionType {
      return pt.precision();
    })
    .def("lod", lod_getter)
    .def("set_lod", lod_setter)
    .def("resize", [](Tensor &tensor, const py::tuple& t) -> void {
      tensor.Resize(tuple_to_vector<int64_t>(t));
    })
    .def("set_data",[](Tensor &pt, py::array array) -> void{
      // std::cout << "set_data : array \n";
      auto buf = array.request();
      // std::cout << "buf.format:" << buf.format << "\n";
      pt.Resize(buf.shape);
      auto format = buf.format;
      if (format == "f"){
        copy_data<float>(pt, buf);
      }
      if (format == "i"){
        copy_data<int>(pt, buf);
        // const int* data = pt.data<int>();
        // int* numd = (int*)buf.ptr;
        // std::cout << numd[0] << " : " << numd[1] << std::endl;
        // std::cout << data[0] << " | " << data[1] << std::endl;
      }
    })
    .def("set_data",[](Tensor &pt, py::array_t<float>& array) -> void{
      auto buf = array.request();
      pt.Resize(buf.shape);
      auto strides = buf.strides;
      if (strides[0] == buf.size * sizeof(float)) {
        memcpy(pt.mutable_data<float>(), buf.ptr, buf.size * sizeof(float));
      } else {
        int last = strides.size() - 1;
        std::vector<int> stride_shape(last);
        int pre = 4;
        for (int i = 0; i < strides.size(); i++ ) {
          stride_shape[last - i] = strides[last - i] / pre;
          pre *= stride_shape[last - i];
        }
        std::vector<int> iterations(strides.size());
        for (int i = 0; i < iterations.size(); i++ ) {
          std::cout << ":" << iterations[i] << std::endl;
        }
        std::cout << "not a dense numpy array\n";
        exit(-1);
      }
    })
    .def("data",[](Tensor &pt) -> py::array_t<float>{
      auto shape = pt.shape();
      return py::array_t<float>(shape, pt.data<float>());;
    })
    .def_buffer([](Tensor &pt) -> py::buffer_info {
      std::vector<int> strides;
      strides.resize(pt.shape().size());
      auto rit_shape = pt.shape().rbegin();
      auto rit_strides = strides.rbegin();
      *rit_strides = sizeof(float);// TODO
      rit_strides++;
      for (; rit_strides != strides.rend(); ++rit_strides, ++rit_shape) {
        *rit_strides = (*(rit_strides - 1)) * (*rit_shape);
      }
      return py::buffer_info(
        (float *)pt.data<float>(),// TODO
        pt.shape(),
        strides
      );
    });
}

void py_bind_config(py::module& m) {
  py::class_<CxxConfig>(m, "CxxConfig")
    .def(py::init())
    .def("set_valid_places", [](CxxConfig& config, const py::tuple& t) -> void {
      config.set_valid_places(tuple_to_vector<Place>(t));
    })
    .def("set_model_file", &CxxConfig::set_model_file)
    .def("set_param_file", &CxxConfig::set_param_file)
    .def("set_model_dir", [](CxxConfig& config, const std::string& model_dir) -> void {
      config.set_model_dir(model_dir);
    })
    .def("set_model_buffer", [](CxxConfig& config, py::array_t<char>& model, py::array_t<char>& params) -> void {
      auto model_buf = model.request();
      auto param_buf = params.request();
      config.set_model_buffer((char*)model_buf.ptr, model_buf.size, (char*)param_buf.ptr, param_buf.size);
    });
    // .def("set_cpu_math_library_num_threads", &CxxConfig::set_cpu_math_library_num_threads);
}

void py_bind_predictor(py::module& m) {
  m.def("CreatePaddlePredictor", [](CxxConfig& config) -> std::unique_ptr<PredictorWrapper> {
    auto p = lite_api::CreatePaddlePredictor<CxxConfig>(config);
    auto x = std::unique_ptr<PredictorWrapper>(new PredictorWrapper());
    x->p_ = p;
    return std::move(x);
  }, py::return_value_policy::take_ownership);

  py::class_<PredictorWrapper>(m, "PaddlePredictor")
    .def("run", &PredictorWrapper::run)
    .def("get_input", &PredictorWrapper::getInput)
    .def("get_output", &PredictorWrapper::getOutput)
    // .def("get_input_names", &PredictorWrapper::GetInputNames)
    // .def("get_output_names", &PredictorWrapper::GetOutputNames)
    // .def("get_input_by_name", &PredictorWrapper::GetInputByName)
    // .def("get_tensor", &PredictorWrapper::GetTensor)
    ;
}

void BindLiteApi(pybind11::module& m){
  py_bind_enums(m);
  py_bind_tensor(m);
  py_bind_config(m);
  py_bind_predictor(m);
}

}  // namespace pybind
}  // namespace lite
}  // namespace paddle
