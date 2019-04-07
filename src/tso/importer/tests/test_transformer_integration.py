from tso.importer import transformer
from tso.importer import data_importer
from tso.observation import observation_request
from sys import maxsize as MAX_SIZE


class TestTransformerIntegration:
    """
    Test Transformer Integration

    These Tests use the data importer directly, so they are integration tests
    """

    def test_transformer_validate_block(self):
        observations = data_importer.get_all_observations()
        for o in observations:
            assert transformer.validate_block(o) is True

    def test_transformer_block_to_request(self):
        observations = data_importer.get_all_observations()
        for o in observations:
            request = transformer.block_to_request(o)
            assert isinstance(request, observation_request.ObservationRequest)

    def test_transformer_transform_cfht_observing_block(self):
        cfht_observations = data_importer.get_all_observations()
        requests = transformer.transform_cfht_observing_blocks(cfht_observations)
        for r in requests:
            assert isinstance(r, observation_request.ObservationRequest)