# qe-ceph-manifest

This repository contains the details of the tested / testing Ceph component
versions against each release.

It is used by IBM Storage Ceph QE and CI systems for deploying the necessary
test environments.

## Schema

The schema of a manifest file is

```yaml
nightly:
  version: <ceph-version>
  repositories:
    <os-release>: <repo-link>
  images:
    ceph-base: <container-registry-namespace>
    <images...>: <container-registry-namesapce>

# Only for released versions of Red Hat platform
  repo_ids:
    <platform>: <ceph-repo-id-for-platform>
```

## Keys - Level 1

The root level keys that map to `--build-type` in `cephci`

| Key | Description | Type |
| --- | ----------- | ---- |
| nightly | Contains details of the last nightly build. | `map` |
| stable | Contains details of nightly build that has passed Sanity test suite | `map` |
| released | Contains details of the latest general availability. | `map` |
| z`N` | Contains details of the `N` z stream generally available. | `map` |

### Keys - Level 2

| Key | Description | Type |
| --- | ----------- | ---- |
| version | Ceph NVR based on ceph-common | `str` |
| repositories | Key value pairs of RPM repo links or `baseurl` for supported platforms | `map` |
| images | Key value pairs of Container images | `map` |

## Usage

Enable `cephci` to pick the right manifest using the below options

```
--product     The product to be deployed which <community | ibm | ceph>
--release     The product version to be deployed. Example <8.1 | 7.0>
--build-type  The type of build to be deployed. Example <nightly | stable | released | z1>
--platform    The test environment platform. Example <rhel-9 | centos-9>
```
