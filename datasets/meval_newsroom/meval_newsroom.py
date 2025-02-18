import json

import datalabs
from datalabs import get_task, TaskType
from datalabs.features import Sequence, Value

_DESCRIPTION = """\
NEWSROOM (meta-evaluation) dataset contains 60 articles with summaries generated by 7 
different methods are annotated with human scores in terms of coherence, fluency, 
informativeness, relevance.
"""

_CITATION = """\
@inproceedings{grusky-etal-2018-newsroom,
    title = "{N}ewsroom: A Dataset of 1.3 Million Summaries with Diverse Extractive Strategies",
    author = "Grusky, Max  and
      Naaman, Mor  and
      Artzi, Yoav",
    booktitle = "Proceedings of the 2018 Conference of the North {A}merican Chapter of the Association for Computational Linguistics: Human Language Technologies, Volume 1 (Long Papers)",
    month = jun,
    year = "2018",
    address = "New Orleans, Louisiana",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/N18-1065",
    doi = "10.18653/v1/N18-1065",
    pages = "708--719",
    abstract = "We present NEWSROOM, a summarization dataset of 1.3 million articles and summaries written by authors and editors in newsrooms of 38 major news publications. Extracted from search and social media metadata between 1998 and 2017, these high-quality summaries demonstrate high diversity of summarization styles. In particular, the summaries combine abstractive and extractive strategies, borrowing words and phrases from articles at varying rates. We analyze the extraction strategies used in NEWSROOM summaries against other datasets to quantify the diversity and difficulty of our new data, and train existing methods on the data to evaluate its utility and challenges. The dataset is available online at summari.es.",
}
"""

_TEST_DOWNLOAD_URL = "https://datalab-hub.s3.amazonaws.com/meval/newsroom/test.jsonl"


class MevalNewsroomConfig(datalabs.BuilderConfig):


    def __init__(
        self,
        evaluation_aspect = None,
        **kwargs
    ):
        super(MevalNewsroomConfig, self).__init__(**kwargs)
        self.evaluation_aspect = evaluation_aspect


class MevalNewsroom(datalabs.GeneratorBasedBuilder):

    evaluation_aspects = [
        "coherence",
        "fluency",
        "informativeness",
        "relevance"
    ]

    BUILDER_CONFIGS = [MevalNewsroomConfig(
        name=aspect,
        version=datalabs.Version("1.0.0"),
        evaluation_aspect=aspect
    ) for aspect in evaluation_aspects]


    def _info(self):
        features = datalabs.Features(
            {
                "source": Value("string"),
                "references": Sequence(Value("string")),
                "hypotheses": Sequence({
                    "system_name": Value("string"),
                    "hypothesis": Value("string")
                }
                ),
                "scores": Sequence(Value("float")),
            }
        )
        return datalabs.DatasetInfo(
            description=_DESCRIPTION,
            features=features,
            homepage="https://lil.nlp.cornell.edu/newsroom/index.html",
            citation=_CITATION,
            languages=["en"],
            task_templates=[
                get_task(TaskType.meta_evaluation_nlg)(
                    source_column="source",
                    hypotheses_column="hypotheses",
                    references_column="references",
                    scores_column = "scores",
                )
            ]
        )

    def _split_generators(self, dl_manager):
        test_path = dl_manager.download_and_extract(_TEST_DOWNLOAD_URL)
        return [
            datalabs.SplitGenerator(
                name=datalabs.Split.TEST, gen_kwargs={"filepath": test_path}
            ),
        ]

    def _generate_examples(self, filepath):
        """ Generate Newsroom examples."""
        with open(filepath, "r", encoding="utf-8") as f:
            for id_, line in enumerate(f.readlines()):
                line = line.strip()
                line = json.loads(line)
                source, hypotheses_scores, references = line["source"], line["hypotheses"], line["references"]
                hypotheses = [ {"system_name":x["system_name"],
                                "hypothesis":x["hypothesis"]} for x in hypotheses_scores]
                scores = [x["scores"][self.config.name] for x in hypotheses_scores]
                yield id_, {
                    "source": source,
                    "hypotheses": hypotheses,
                    "references": references,
                    "scores": scores,
                }
