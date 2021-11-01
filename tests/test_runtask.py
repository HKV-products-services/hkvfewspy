import hkvfewspy as hkv
import datetime


def test_runtask_params():
    pi = hkv.Pi(protocol="rest")
    pi.setUrl(
        "https://oms-ijmuiden.hkvservices.nl/FewsWebServices/rest/fewspiservice/v1/"
    )

    pi.runTask(
        startTime=datetime.date(2021, 10, 30),
        endTime=datetime.date(2021, 11, 1),
        workflowId="wf.sym.DatabaseMaintenance",
    )
    assert pi
