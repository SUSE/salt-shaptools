# kudos:
#   - https://medium.com/@exustash/three-good-practices-for-better-ci-cd-makefiles-5b93452e4cc3
#   - https://le-gall.bzh/post/makefile-based-ci-chain-for-go/
#   - https://makefiletutorial.com/
#   - https://www.cl.cam.ac.uk/teaching/0910/UnixTools/make.pdf
#
SHELL := /usr/bin/env bash # set default shell
.SHELLFLAGS = -c # Run commands in a -c flag 

.NOTPARALLEL: ;          # wait for this target to finish
.EXPORT_ALL_VARIABLES: ; # send all vars to shell

.PHONY: all # All targets are accessible for user
.DEFAULT: help # Running Make will run the help target

BRANCH := $(shell git rev-parse --abbrev-ref HEAD)
ifeq ($(BRANCH), HEAD)
	BRANCH := ${CI_BUILD_REF_NAME}
endif

# help: @ List available tasks of the project
help:
	@grep -E '[a-zA-Z\.\-]+:.*?@ .*$$' $(MAKEFILE_LIST)| tr -d '#'  | awk 'BEGIN {FS = ":.*?@ "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

## test section
# All tests are called on "." if possible.
# If this is not possible a special loop is used
# to sum up all error codes.

# test: @ Run all defined tests
test: test-tab test-codespell test-shellcheck test-yamllint test-jsonlint test-python
	@echo "All tests Done!"

# test-tab: @ Run linting to find files containing tabspaces
test-tab:
	@for file in $(shell find . -regextype egrep -regex '.*\.(sls|yml|yaml)' ! -path "**/venv/*" ! -path "**/saltvirtenv/*"); do\
		grep -q -P '\t' $${file} ;\
		if [ "$$?" -eq 0 ]; then\
			err_add=1 ;\
			echo "Tab found in $${file}" ;\
			grep -H -n -P '\t' $${file} ;\
		else \
			err_add=0 ;\
		fi;\
		err=$$((err_add + err)) ;\
	done; exit $$err

# test-codespell: @ Run spell check
test-codespell:
	codespell -H -f -s -I .codespell.ignore.words -S $(shell cat .codespell.ignore.files) -C 4 -q 6

# test-shellcheck: @ Run linting on all shell scripts
test-shellcheck:
	for file in $(shell find . -name '*.sh' ! -path "**/venv/*" ! -path "**/saltvirtenv/*"); do\
		echo $${file} ;\
		shellcheck -s bash -x $${file};\
		err=$$(($$? + err)) ;\
	done; exit $$err

# test-yamllint: @ Run linting on all yaml files
test-yamllint:
	# yamllint -c .yamllint.yaml -s .
	yamllint -c .yamllint.yaml .

# test-jsonlint: @ Run linting on all json files
test-jsonlint:
	for file in $(shell find . -name '*.json' ! -path "**/venv/*" ! -path "**/saltvirtenv/*" ! -path "**/htmlcov/*"); do\
		echo $${file} ;\
		jq << $${file} >/dev/null;\
		err=$$(($$? + err)) ;\
	done; exit $$err

# test-mlc: @ Run markup link checker
test-mlc:
	mlc --throttle 1000

# test-python: @ Run Python Unit Tests
test-python:
	./tests/run.sh

# all: @ Runs everything
all: test
