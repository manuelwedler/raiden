import structlog
from eth_utils import decode_hex, is_binary_address, to_canonical_address

from raiden.network.rpc.client import JSONRPCClient, check_address_has_code
from raiden.utils.typing import (
    Address,
    BlockSpecification,
    MonitoringServiceAddress,
    ServiceRegistryAddress,
    TokenAddress,
    TokenNetworkRegistryAddress,
)
from raiden_contracts.constants import CONTRACT_MONITORING_SERVICE
from raiden_contracts.contract_manager import ContractManager

log = structlog.get_logger(__name__)


class MonitoringService:
    def __init__(
        self,
        jsonrpc_client: JSONRPCClient,
        monitoring_service_address: MonitoringServiceAddress,
        contract_manager: ContractManager,
        block_identifier: BlockSpecification,
    ):
        if not is_binary_address(monitoring_service_address):
            raise ValueError("Expected binary address for monitoring service")

        self.contract_manager = contract_manager
        check_address_has_code(
            client=jsonrpc_client,
            address=Address(monitoring_service_address),
            contract_name=CONTRACT_MONITORING_SERVICE,
            expected_code=decode_hex(
                contract_manager.get_runtime_hexcode(CONTRACT_MONITORING_SERVICE)
            ),
            given_block_identifier=block_identifier,
        )

        proxy = jsonrpc_client.new_contract_proxy(
            abi=self.contract_manager.get_contract_abi(CONTRACT_MONITORING_SERVICE),
            contract_address=Address(monitoring_service_address),
        )

        self.address = monitoring_service_address
        self.proxy = proxy
        self.client = jsonrpc_client
        self.node_address = self.client.address

    def token_network_registry_address(
        self, block_identifier: BlockSpecification
    ) -> TokenNetworkRegistryAddress:
        return TokenNetworkRegistryAddress(
            to_canonical_address(
                self.proxy.contract.functions.token_network_registry().call(
                    block_identifier=block_identifier
                )
            )
        )

    def token_address(self, block_identifier: BlockSpecification) -> TokenAddress:
        return TokenAddress(
            to_canonical_address(
                self.proxy.contract.functions.token().call(block_identifier=block_identifier)
            )
        )

    def service_registry_address(
        self, block_identifier: BlockSpecification
    ) -> ServiceRegistryAddress:
        return ServiceRegistryAddress(
            to_canonical_address(
                self.proxy.contract.functions.service_registry().call(
                    block_identifier=block_identifier
                )
            )
        )
