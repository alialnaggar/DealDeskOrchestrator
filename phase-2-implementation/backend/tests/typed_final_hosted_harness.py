"""Test-tree-only synthetic sender; never constructs or imports a live HTTP sender."""

from dealdesk_phase2.live_models import ProviderError
from dealdesk_phase2.typed_final_hosted import _run_assessment


class MockTypedTransport:
    def __init__(self, replies):
        self.replies = list(replies)
        self.requests = []

    def send(self, body):
        self.requests.append(body)
        if not self.replies:
            raise ProviderError("transport_failure")
        answer = self.replies.pop(0)
        return answer(body) if callable(answer) else answer


def run_mock(original, config, adapter, *, _mock_transport, authorized=False,
             owner_billing_attested=False, **kwargs):
    if type(_mock_transport) is not MockTypedTransport or authorized is not True or (
            owner_billing_attested is not True):
        raise ValueError("test_harness_authorization_required")
    return _run_assessment(original, config, adapter, send=_mock_transport.send,
        credential_digest="offline-mock-no-credential", exclusive_databases=False, **kwargs)
