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
    default:
      <os-release>: <repo-link>
    eu-de:
      <os-release>: <repo-link>
    tucson:
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
| nightly | Contains details of the last nightly / CI build. | `map` |
| stable | Contains details of a nightly build that has passed the Sanity test suite. | `map` |
| rc | Contains details of the release-candidate build. | `map` |
| respin | Contains details of a ceph respin on the latest release. | `map` |
| released | Contains details of the latest general availability. | `map` |
| z`N` | Contains details of the `N` z-stream generally available build. | `map` |

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
--release     The product version to be deployed. Example <9.2 | 8.1 | 7.1>
--build-type  The type of build to be deployed. Example <nightly | stable | rc | respin | released | z1>
--platform    The test environment platform. Example <rhel-9 | rhel-10 | centos-9>
```

## Notes

Key points to remember

### Container registries

- IBM production (`ibm-prod`) uses `cp.icr.io` (for `released` / `z0` / `z1` / `zN`)
- IBM staging / preprod (`ibm-stage`) uses `preprod.icr.io` (for `nightly` / `stable` / `rc` / `respin`)
- `cp.stg.icr.io` is decommissioned; replace any remaining references with `preprod.icr.io`
- Red Hat production (`rh-prod`) uses `registry.redhat.io` (for `released` / `z0` / `z1` / `zN`)
- Red Hat staging uses `registry.stage.redhat.io` (for `stable` / `rc` / `respin`; some `nightly` / `stable` sections still use `quay.io`)
- Legacy Red Hat engineering proxy: `registry-proxy.engineering.redhat.com`
- Community Ceph images typically use `quay.ceph.io` / `quay.io`

### Section conventions

- `nightly` points to the latest CI / testing build (not GA content)
- `stable` points to a sanity-passed testing build (IBM: `preprod.icr.io`; RH: often `registry.stage.redhat.io` or `quay.io`)
- `rc` points to the release-candidate content used before GA
- `respin` points to respin builds of a released stream (repos may be GA; images may still be `preprod.icr.io` until promoted)
- `released` and `zN` point to generally available content with production registries and public-facing repositories
- IBM public repos are under `https://public.dhe.ibm.com/ibmdl/export/pub/storage/ceph/`
- Lab mirrors for IBM use `http://repo.qe.ceph.lab/repos/ceph/{testing|released}/ibm/...`

Ensure the local Container Registry holds the necessary images.
