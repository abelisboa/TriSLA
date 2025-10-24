package main

import (
  "encoding/json"
  "fmt"
  "github.com/hyperledger/fabric-contract-api-go/contractapi"
)

type SLAContract struct{ contractapi.Contract }

type SLA struct {
  SLAID      string `json:"sla_id"`
  SliceType  string `json:"slice_type"`
  Decision   string `json:"decision"`
  Timestamp  string `json:"timestamp"`
  Compliance string `json:"compliance"`
}

func (s *SLAContract) RegisterSLA(ctx contractapi.TransactionContextInterface,
  id, slice, dec, ts, comp string) error {

  b, _ := json.Marshal(SLA{id, slice, dec, ts, comp})
  return ctx.GetStub().PutState(id, b)
}

func (s *SLAContract) QuerySLA(ctx contractapi.TransactionContextInterface, id string) (*SLA, error) {
  b, err := ctx.GetStub().GetState(id)
  if err != nil || b == nil {
    return nil, fmt.Errorf("SLA %s não encontrado", id)
  }
  var sla SLA
  _ = json.Unmarshal(b, &sla)
  return &sla, nil
}

func main() {
  cc, err := contractapi.NewChaincode(new(SLAContract))
  if err != nil {
    panic(err)
  }
  if err := cc.Start(); err != nil {
    panic(err)
  }
}
