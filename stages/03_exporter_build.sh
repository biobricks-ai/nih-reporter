#!/bin/bash

set -eu
export LC_ALL=C

export downloaddir='download'
export rawdir='raw'
export brickdir_exporter='brick/ExPORTER'

{ [ -d "$rawdir" ] && rm -Rf "$rawdir"; }  || true
mkdir -p "$rawdir"

mkdir -p "$brickdir_exporter"


# Exit function to clean up temporary directory
function cleanup() {
	echo "Cleaning up raw directory..."
	rm -rf "$rawdir"
	exit ${1:-0}
}

# Set trap to ensure cleanup on exit, interrupt, or error
trap 'cleanup $?' EXIT INT TERM




function process_by_group_prefix() {
	export D_GROUP="$( echo $1 | cut -d/ -f1)"
	export D_PREFIX="$(echo $1 | cut -d/ -f2)"
	ls $downloaddir/${D_GROUP}/${D_PREFIX}_*.zip | parallel --bar '
		outputdir=${rawdir}/${D_GROUP}/${D_PREFIX};
		mkdir -p $outputdir
		unzip -d ${outputdir} {}
	'
}

function process_by_group_prefix_with_fy() {
	export D_GROUP="$( echo $1 | cut -d/ -f1)"
	export D_PREFIX="$(echo $1 | cut -d/ -f2)"
	ls $downloaddir/${D_GROUP}/${D_PREFIX}_*.zip | parallel --bar '
		FY={= ($_) = /FY(\d{4})/; =}
		outputdir=${rawdir}/${D_GROUP}/${D_PREFIX}/FY=${FY};
		mkdir -p $outputdir
		unzip -d ${outputdir} {}
	'
}

function myenvsubst() {
	envsubst '$rawdir,$brickdir_exporter'
}

# ExPORTER/projects/RePORTER_PRJ_C {{{
process_by_group_prefix projects/RePORTER_PRJ_C

mkdir -p "$brickdir_exporter/projects"
duckdb -c "$(myenvsubst <<'SQL'
COPY (
	SELECT
		*
	FROM read_csv(
		'${rawdir}/projects/RePORTER_PRJ_C/*.csv',
		encoding = 'utf-8',
		header = true,
		quote = '"',
		escape = '"',
		union_by_name = true
	)
) TO '${brickdir_exporter}/projects/RePORTER_PRJ_C.parquet' (FORMAT parquet, PARTITION_BY (FY));
SQL
)"
# }}}

# ExPORTER/projects/RePORTER_PRJFUNDING_C {{{
process_by_group_prefix projects/RePORTER_PRJFUNDING_C

mkdir -p "$brickdir_exporter/projects"
duckdb -c "$(myenvsubst <<'SQL'
COPY (
	SELECT
		*
	FROM read_csv(
		'${rawdir}/projects/RePORTER_PRJFUNDING_C/*.csv',
		encoding = 'utf-8',
		header = true,
		quote = '"',
		escape = '"',
		union_by_name = true
	)
) TO '${brickdir_exporter}/projects/RePORTER_PRJFUNDING_C.parquet' (FORMAT parquet, PARTITION_BY (FY));
SQL
)"
# }}}

# ExPORTER/abstracts/RePORTER_PRJABS_C {{{
process_by_group_prefix_with_fy abstracts/RePORTER_PRJABS_C

#file ${rawdir}/abstracts/RePORTER_PRJABS_C/FY\=*/*.csv | grep -P 'ASCII|ISO-8859' | cut -d: -f1 | xargs -P$(nproc) recode -v ISO-8859-1..UTF-8
#find ${rawdir}/abstracts/RePORTER_PRJABS_C/ -type f | xargs -P$(nproc)  recode -v ISO-8859-1..UTF-8
find ${rawdir}/abstracts/RePORTER_PRJABS_C/ -type f -name '*.csv' | sort | parallel --bar -k '
	FY={= ($_) = m</FY=(\d{4})/> =};
	{ [ "$FY" -le 2021 ] && recode -v ISO-8859-1..UTF-8 {} ; } || true;
'

mkdir -p "$brickdir_exporter/abstracts"
duckdb -c "$(myenvsubst <<'SQL'
COPY (
	SELECT
		*
	FROM read_csv(
		'${rawdir}/abstracts/RePORTER_PRJABS_C/**/*.csv',
		header = true,
		strict_mode = false,
		quote = '"',
		escape = '"',
		union_by_name = true,
		hive_partitioning = true
	)
) TO '${brickdir_exporter}/abstracts/RePORTER_PRJABS_C.parquet' (FORMAT parquet, PARTITION_BY (FY));
SQL
)"
# }}}

# ExPORTER/clinicalstudies/ClinicalStudies {{{

# read the single file directly
mkdir -p "$brickdir_exporter/clinicalstudies"
duckdb -c "$(myenvsubst <<'SQL'
COPY (
	SELECT
		*
	FROM read_csv(
		'download/clinicalstudies/ClinicalStudies.csv',
		header = true,
		quote = '"',
		escape = '"'
	)
) TO '${brickdir_exporter}/clinicalstudies/ClinicalStudies.parquet' (FORMAT parquet);
SQL
)"
# }}}

# vim: fdm=marker
