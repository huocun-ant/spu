# Copyright 2023 Ant Group Co., Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import jax
import jax.numpy as jnp


class OneVsRestClassifier:
    def __init__(
        self,
        n_classes,
        base_estimate_cls=None,
        estimators=None,
        **kwargs,
    ):
        self.classes_ = n_classes

        if estimators is not None:
            self.estimators_ = estimators
        else:
            if base_estimate_cls is None:
                raise ValueError("base_estimator must be provided")
            self.estimators_ = [base_estimate_cls(**kwargs) for _ in range(n_classes)]

    def tree_flatten(self):
        static_data = (self.classes_,)
        dynamic_data = (self.estimators_,)
        return (dynamic_data, static_data)

    @classmethod
    def tree_unflatten(cls, static_data, dynamic_data):
        (classes,) = static_data
        (estimators,) = dynamic_data

        return cls(classes, estimators=estimators)

    def fit(self, X, y):
        for i in range(self.classes_):
            self.estimators_[i].fit(X, jnp.where(y == i, 1, 0))

    def predict(self, X_test):
        maxima = []
        for i in range(self.classes_):
            maxima.append(self.estimators_[i].predict_proba(X_test)[:, 1])
        maxima = jnp.array(maxima)
        return maxima.argmax(axis=0)

    def predict_proba(self, X_test):
        maxima = []
        for i in range(self.classes_):
            maxima.append(self.estimators_[i].predict_proba(X_test)[:, 1])
        maxima = jnp.array(maxima)

        return maxima.T


jax.tree_util.register_pytree_node_class(OneVsRestClassifier)
