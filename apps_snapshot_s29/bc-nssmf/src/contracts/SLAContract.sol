// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/*
 *  TriSLA – SLA Smart Contract (Modelo Avançado)
 *  - Alinhado ao Capítulo 6 da dissertação
 *  - Suporta SLA struct, SLO list, auditoria, eventos, atualização de status
 */

contract SLAContract {

    enum SLAStatus { REQUESTED, APPROVED, REJECTED, ACTIVE, COMPLETED }

    struct SLO {
        string name;
        uint256 value;
        uint256 threshold;
    }

    struct SLA {
        uint256 id;
        string customer;
        string serviceName;
        bytes32 slaHash;
        SLAStatus status;
        SLO[] slos;
        uint256 createdAt;
        uint256 updatedAt;
    }

    uint256 private nextId = 1;
    mapping(uint256 => SLA) public slas;

    event SLARequested(uint256 indexed slaId, string customer, string serviceName);
    event SLAUpdated(uint256 indexed slaId, SLAStatus status);
    event SLACompleted(uint256 indexed slaId);

    function registerSLA(
        string memory customer,
        string memory serviceName,
        bytes32 slaHash,
        SLO[] memory slosInput
    ) public returns (uint256) {

        uint256 id = nextId;

        SLA storage sla = slas[id];
        sla.id = id;
        sla.customer = customer;
        sla.serviceName = serviceName;
        sla.slaHash = slaHash;
        sla.status = SLAStatus.REQUESTED;
        sla.createdAt = block.timestamp;
        sla.updatedAt = block.timestamp;

        for (uint256 i = 0; i < slosInput.length; i++) {
            sla.slos.push(
                SLO({
                    name: slosInput[i].name,
                    value: slosInput[i].value,
                    threshold: slosInput[i].threshold
                })
            );
        }

        nextId += 1;

        emit SLARequested(id, customer, serviceName);
        return id;
    }

    function updateSLAStatus(uint256 slaId, SLAStatus newStatus) public {
        require(slas[slaId].id != 0, "SLA not found");

        slas[slaId].status = newStatus;
        slas[slaId].updatedAt = block.timestamp;

        emit SLAUpdated(slaId, newStatus);

        if (newStatus == SLAStatus.COMPLETED) {
            emit SLACompleted(slaId);
        }
    }

    function getSLA(uint256 slaId) public view returns (
        string memory customer,
        string memory serviceName,
        SLAStatus status,
        uint256 createdAt,
        uint256 updatedAt
    ) {
        require(slas[slaId].id != 0, "SLA not found");
        SLA storage sla = slas[slaId];

        return (
            sla.customer,
            sla.serviceName,
            sla.status,
            sla.createdAt,
            sla.updatedAt
        );
    }
}
