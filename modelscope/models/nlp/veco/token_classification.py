# Copyright 2019 Facebook AI Research and the HuggingFace Inc. team.
# Copyright (c) 2018, NVIDIA CORPORATION.
# Copyright 2021-2022 The Alibaba DAMO NLP Team Authors.
# All rights reserved.
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

from transformers import RobertaForTokenClassification

from modelscope.metainfo import Models
from modelscope.models import Model, TorchModel
from modelscope.models.builder import MODELS
from modelscope.outputs import AttentionTokenClassificationModelOutput
from modelscope.utils.constant import Tasks
from modelscope.utils.hub import parse_label_mapping
from .configuration import VecoConfig


@MODELS.register_module(Tasks.token_classification, module_name=Models.veco)
class VecoForTokenClassification(TorchModel, RobertaForTokenClassification):
    """Veco Model with a token classification head on top (a linear layer on top of the hidden-states output) e.g.
    for Named-Entity-Recognition (NER) tasks.

    This model inherits from [`PreTrainedModel`]. Check the superclass documentation for the generic
    methods the library implements for all its model (such as downloading or saving, resizing the input embeddings,
    pruning heads etc.)

    This model is also a PyTorch [torch.nn.Module](https://pytorch.org/docs/stable/nn.html#torch.nn.Module)
    subclass. Use it as a regular PyTorch Module and refer to the PyTorch documentation for all matter related to
    general usage and behavior.

    Parameters:
        config ([`VecoConfig`]): Model configuration class with all the parameters of the
            model. Initializing with a config file does not load the weights associated with the model, only the
            configuration. Check out the [`~PreTrainedModel.from_pretrained`] method to load the model
            weights.

    This class overrides [`RobertaForTokenClassification`]. Please check the superclass for the
    appropriate documentation alongside usage examples.
    """

    config_class = VecoConfig

    def __init__(self, config, **kwargs):
        super().__init__(config.name_or_path, **kwargs)
        super(Model, self).__init__(config)

    def forward(self, *args, **kwargs):
        kwargs['return_dict'] = True
        outputs = super(Model, self).forward(*args, **kwargs)
        return AttentionTokenClassificationModelOutput(
            loss=outputs.loss,
            logits=outputs.logits,
            hidden_states=outputs.hidden_states,
            attentions=outputs.attentions,
        )

    @classmethod
    def _instantiate(cls, **kwargs):
        """Instantiate the model.

        Args:
            kwargs: Input args.
                    model_dir: The model dir used to load the checkpoint and the label information.
                    num_labels: An optional arg to tell the model how many classes to initialize.
                                    Method will call utils.parse_label_mapping if num_labels is not input.
                    label2id: An optional label2id mapping, which will cover the label2id in configuration (if exists).

        Returns:
            The loaded model, which is initialized by transformers.PreTrainedModel.from_pretrained
        """

        model_dir = kwargs.pop('model_dir', None)
        if model_dir is None:
            config = VecoConfig(**kwargs)
            model = cls(config)
        else:
            model_kwargs = {}
            label2id = kwargs.get('label2id', parse_label_mapping(model_dir))
            id2label = kwargs.get(
                'id2label', None if label2id is None else
                {id: label
                 for label, id in label2id.items()})
            if id2label is not None and label2id is None:
                label2id = {label: id for id, label in id2label.items()}

            num_labels = kwargs.get(
                'num_labels', None if label2id is None else len(label2id))
            if num_labels is not None:
                model_kwargs['num_labels'] = num_labels
            if label2id is not None:
                model_kwargs['label2id'] = label2id
            if id2label is not None:
                model_kwargs['id2label'] = id2label
            model = super(Model, cls).from_pretrained(
                pretrained_model_name_or_path=model_dir, **model_kwargs)
        return model
