import logging
import json
import requests
log = logging.getLogger(__name__)


def merge(job_settings, default_settings):
    """ Merge two dicts

    :param job_settings:
    :param default_settings:
    :return:
    """
    settings = default_settings
    if settings is None:
        settings = {}
    settings.update(job_settings)
    return settings


def new_deploy(job_name, job_file):
    """Deploys new chronos job given file

    :param job_name: job name
    :param job_file: file to be sent as request body
    :return:
    """
    chronos_uri = _address()
    with open(job_file, 'r') as content_file:
        content = content_file.read()
    job_attr = json.loads(content)
    endpoint = _get_endpoint_name(job_attr)
    if not _is_deployed(job_name, chronos_uri):
        post_url = chronos_uri + '/scheduler/' + endpoint
        log.warn('New deploy: ' + str(post_url) + ' ' + str(job_attr))
        r = requests.post(post_url, headers={'Content-Type': 'application/json'}, data=json.dumps(job_attr))
        return str(r.status_code) + ', ' + r.text
    else:
        return None


def re_deploy(job_name, job_file):
    """Redeploys chronos job given file

    :param job_name: job name
    :param job_file: file to be sent as request body
    :return:
    """
    with open(job_file, 'r') as content_file:
        content = content_file.read()
    job_attr = json.loads(content)
    chronos_uri = _address()
    endpoint = _get_endpoint_name(job_attr)
    if _is_deployed(job_name, chronos_uri):
        put_url = chronos_uri + '/scheduler/' + endpoint
        log.warn('Re deploy: ' + str(put_url) + ' ' + str(job_attr))
        r = requests.put(put_url, headers={'Content-Type': 'application/json'}, data=json.dumps(job_attr))
        return str(r.status_code) + ', ' + r.text
    else:
        return None


def undeploy(job_name):
    """Undeploy chronos job

    :param job_name: job name
    :return:
    """
    chronos_uri = _address()
    if _is_deployed(job_name):
        r = requests.delete(chronos_uri + '/scheduler/job/' + job_name)
        return str(r.status_code) + ', ' + r.text
    else:
        return None


def _is_deployed(job_name, chronos_uri):
    job = _get_job(job_name, chronos_uri)
    log.warn('Job fetched ' + job_name + ' ' + str(job))
    return not (job is None)


def _address():
    return __salt__['marathon_client.wait_for_healthy_api']('chronos', '/scheduler/jobs')


def _get_job(job_name, chronos_uri):
    r = requests.get(chronos_uri + '/scheduler/jobs')
    if r.status_code == 200:
        jobs = [x for x in r.json() if x['name'] == job_name]
        if (len(jobs) == 0):
            return None
        else:
            return jobs[0]
    else:
        return None


def _get_endpoint_name(job_def):
    parents = job_def.get('parents', [])
    if len(parents) > 0:
        return 'dependency'
    else:
        return 'iso8601'
