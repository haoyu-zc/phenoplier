import numpy as np
import sklearn.datasets as datasets
from sklearn.metrics import adjusted_rand_score as ari
from sklearn.cluster import KMeans

from clustering.ensembles.eac import eac_single, eac_complete, eac_average
from clustering.ensembles.utils import supraconsensus
from clustering.ensembles.measures import anmi, aari


def test_iris():
    # Prepare
    np.random.seed(1)

    data = datasets.load_iris().data
    ref_part = datasets.load_iris().target

    ensemble = np.array(
        [
            KMeans(n_clusters=k, init="random", n_init=1).fit_predict(data)
            for k in range(2, 20)
        ]
    )

    # Run
    consensus_results = supraconsensus(
        ensemble,
        3,
        methods=(eac_single, eac_complete, eac_average),
        selection_criterion=aari,
    )
    consensus_part = consensus_results[0]
    consensus_best_method = consensus_results[1]

    # Validate
    assert consensus_part is not None
    assert consensus_part.shape == (150,)
    assert len(np.unique(consensus_part)) == 3
    assert ari(ref_part, consensus_part) >= 0.70

    assert consensus_best_method in ("eac_single", "eac_complete", "eac_average")

    # Check that the ARI obtained by the consensus partition is
    # greater than any ensemble member
    for ensemble_member in ensemble:
        assert ari(ref_part, consensus_part) > ari(ref_part, ensemble_member)


def test_circles():
    # Prepare
    np.random.seed(1)

    data, ref_part = datasets.make_circles(n_samples=150, factor=0.3, noise=0.05)

    ensemble = np.array(
        [
            KMeans(n_clusters=k, init="random", n_init=1).fit_predict(data)
            for k in range(2, 20)
        ]
    )

    # Run
    consensus_part = supraconsensus(
        ensemble,
        2,
        methods=(eac_single, eac_complete, eac_average),
        selection_criterion=aari,
    )[0]

    # Validate
    assert consensus_part is not None
    assert consensus_part.shape == (150,)
    assert len(np.unique(consensus_part)) == 2
    assert ari(ref_part, consensus_part) >= 0.95

    # Check that the ARI obtained by the consensus partition is
    # greater than any ensemble member
    for ensemble_member in ensemble:
        assert ari(ref_part, consensus_part) > ari(ref_part, ensemble_member)


def test_anmi_criterion():
    # Prepare
    np.random.seed(1)

    data, ref_part = datasets.make_circles(
        n_samples=150, factor=0.3, noise=0.05, random_state=2
    )

    ensemble = np.array(
        [
            KMeans(n_clusters=k, init="random", n_init=1, random_state=0).fit_predict(
                data
            )
            for k in range(2, 10)
        ]
    )

    # Run
    consensus_part = supraconsensus(
        ensemble,
        2,
        methods=(eac_single, eac_complete, eac_average),
        selection_criterion=anmi,
    )[0]

    eac_single_part = eac_single(ensemble, 2)
    eac_complete_part = eac_complete(ensemble, 2)
    eac_average_part = eac_average(ensemble, 2)

    # supraconsensus partition should be one of the others
    assert (
        ari(consensus_part, eac_single_part) == 1.0
        or ari(consensus_part, eac_complete_part) == 1.0
        or ari(consensus_part, eac_average_part) == 1.0
    )

    # ANMI should be greater or equal for the supraconsensus
    consensus_anmi = anmi(ensemble, consensus_part)
    assert consensus_anmi >= anmi(ensemble, eac_single_part)
    assert consensus_anmi >= anmi(ensemble, eac_complete_part)
    assert consensus_anmi >= anmi(ensemble, eac_average_part)


def test_aari_criterion():
    # Prepare
    np.random.seed(1)

    data, ref_part = datasets.make_circles(
        n_samples=150, factor=0.3, noise=0.05, random_state=2
    )

    ensemble = np.array(
        [
            KMeans(n_clusters=k, init="random", n_init=1, random_state=0).fit_predict(
                data
            )
            for k in range(2, 10)
        ]
    )

    # Run
    consensus_part = supraconsensus(
        ensemble,
        2,
        methods=(eac_single, eac_complete, eac_average),
        selection_criterion=aari,
    )[0]

    eac_single_part = eac_single(ensemble, 2)
    eac_complete_part = eac_complete(ensemble, 2)
    eac_average_part = eac_average(ensemble, 2)

    # supraconsensus partition should be one of the others
    assert (
        ari(consensus_part, eac_single_part) == 1.0
        or ari(consensus_part, eac_complete_part) == 1.0
        or ari(consensus_part, eac_average_part) == 1.0
    )

    # AARI should be greater or equal for the supraconsensus
    consensus_anmi = aari(ensemble, consensus_part)
    assert consensus_anmi >= aari(ensemble, eac_single_part)
    assert consensus_anmi >= aari(ensemble, eac_complete_part)
    assert consensus_anmi >= aari(ensemble, eac_average_part)


def test_supraconsensus_returns_stats():
    # Prepare
    np.random.seed(1)

    data = datasets.load_iris().data
    ref_part = datasets.load_iris().target

    ensemble = np.array(
        [
            KMeans(n_clusters=k, init="random", n_init=1).fit_predict(data)
            for k in range(2, 20)
        ]
    )

    consensus_methods = (eac_single, eac_complete, eac_average)
    consensus_methods_names = (
        "eac_single",
        "eac_complete",
        "eac_average",
    )

    # Run
    consensus_part, max_method, max_value = supraconsensus(
        ensemble, 3, methods=consensus_methods, selection_criterion=aari
    )

    # Validate
    assert consensus_part is not None
    assert consensus_part.shape == (150,)
    assert len(np.unique(consensus_part)) == 3
    assert ari(ref_part, consensus_part) >= 0.70

    assert max_method is not None
    assert max_method in consensus_methods_names

    assert max_value > 0.0
    assert max_value < 1.0

    # Check that the ARI obtained by the consensus partition is
    # greater than any ensemble member
    for ensemble_member in ensemble:
        assert ari(ref_part, consensus_part) > ari(ref_part, ensemble_member)

    # check that the max method is correct
    real_max_part = eval(f"{max_method}(ensemble, 3)")
    assert ari(real_max_part, consensus_part) == 1.0
