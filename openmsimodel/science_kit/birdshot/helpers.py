import pandas as pd
from gemd.entity import PerformedSource, FileLink
import subprocess


def gen_compositions(root):
    ids = []
    for id in range(1, 17):
        composition_id = "0%s" % id if id % 10 == id else "%s" % id
        composition_id = str(root).split("/")[-1] + composition_id
        ids.append(composition_id)
    return ids


def return_common_items(composition_id, fabrication_method, batch, yymm=None):
    long_name = (
        f"composition {composition_id} with {fabrication_method} in batch {batch}"
    )
    short_name = f"{composition_id}-{fabrication_method}-{batch}"
    alloy_common_name = "Alloy ({})".format(short_name)
    common_tags = (
        ("composition_id", composition_id),
        ("batch", batch),
        ("fabrication_method", fabrication_method),
    )
    if yymm:
        common_tags = (("yymm", yymm),) + common_tags
    return long_name, short_name, alloy_common_name, common_tags


def substring_after(s, delim):
    return s.partition(delim)[2]


def ingest_aaa_synthesis_results(iteration, synthesis_path, file_links, measurements):
    df = pd.read_excel(synthesis_path)
    file_links["Summary Sheet"] = FileLink(
        filename=str(synthesis_path).split("/")[-1], url=str(synthesis_path)
    )
    new_header = df.iloc[1]
    core_df = df[2:19]
    core_df.columns = new_header
    column_names = list(core_df.columns.values)
    core_df = core_df.reset_index()
    for row_index, row in core_df.iterrows():
        if row_index == 0:
            sub_header_row = row
            continue
        name = row["Alloy"]
        split_name = name.split("_")
        composition_id = split_name[0]
        yymm = split_name[1]
        fabrication_method = split_name[2]
        batch = split_name[3]

        # target composition
        target_composition_column = column_names[1]
        for i in range(2, 8):
            element_name = sub_header_row[i]
            composition = row[i]
            measurements[composition_id][target_composition_column][
                element_name
            ] = composition

        # T05: averaged measured composition and difference
        measurement_id = row[8]
        average_composition_column = column_names[8]
        composition_difference_column = column_names[14]
        for i in range(9, 15):
            element_name = sub_header_row[i]
            average_composition = row[i]
            composition_difference = row[i + 6]
            measurements[composition_id][fabrication_method][batch][measurement_id][
                average_composition_column
            ][element_name] = average_composition
            measurements[composition_id][fabrication_method][batch][measurement_id][
                composition_difference_column
            ][element_name] = composition_difference

        ######## T03: phase/lattice parameters
        measurement_id = row[21]

        lattice_parameter_column = column_names[22 - 1]

        lattice_parameter = row[23 - 1]

        measurements[composition_id][fabrication_method][batch][measurement_id][
            lattice_parameter_column
        ] = lattice_parameter

        # T03: hardness, HV, SD, HV
        measurement_id = row[24 - 1]
        hardness_column = column_names[24 - 1]
        sd_hv_column = column_names[25 - 1]
        hardness = row[25 - 1]
        sd_hv = row[26 - 1]
        measurements[composition_id][fabrication_method][batch][measurement_id][
            hardness_column
        ] = hardness
        measurements[composition_id][fabrication_method][batch][measurement_id][
            sd_hv_column
        ] = sd_hv


def ingest_synthesis_results(iteration, synthesis_path, file_links, measurements):
    df = pd.read_excel(synthesis_path)
    file_links["Summary Sheet"] = FileLink(
        filename=str(synthesis_path).split("/")[-1], url=str(synthesis_path)
    )
    new_header = df.iloc[1]
    core_df = df[2:19]
    core_df.columns = new_header
    column_names = list(core_df.columns.values)
    core_df = core_df.reset_index()
    for row_index, row in core_df.iterrows():
        if row_index == 0:
            sub_header_row = row
            continue
        name = row["Alloy"]
        split_name = name.split("_")
        composition_id = split_name[0]
        yymm = split_name[1]
        fabrication_method = split_name[2]
        batch = split_name[3]

        # target composition
        target_composition_column = column_names[1]
        for i in range(2, 8):
            element_name = sub_header_row[i]
            composition = row[i]
            measurements[composition_id][target_composition_column][
                element_name
            ] = composition

        # T05: averaged measured composition and difference
        measurement_id = row[8]
        average_composition_column = column_names[8]
        composition_difference_column = column_names[14]
        for i in range(9, 15):
            element_name = sub_header_row[i]
            average_composition = row[i]
            composition_difference = row[i + 6]
            measurements[composition_id][fabrication_method][batch][measurement_id][
                average_composition_column
            ][element_name] = average_composition
            measurements[composition_id][fabrication_method][batch][measurement_id][
                composition_difference_column
            ][element_name] = composition_difference

        # T03: phase/lattice parameters
        measurement_id = row[21]
        phase_column = column_names[21]
        lattice_parameter_column = column_names[22]
        phase = row[22]
        lattice_parameter = row[23]

        measurements[composition_id][fabrication_method][batch][measurement_id][
            phase_column
        ] = phase
        measurements[composition_id][fabrication_method][batch][measurement_id][
            lattice_parameter_column
        ] = lattice_parameter

        # T03: hardness, HV, SD, HV
        offset = 0
        if 'AAA' in synthesis_path:
            offset = 1
        measurement_id = row[24 - offset]
        hardness_column = column_names[24 - offset]
        sd_hv_column = column_names[25 - offset]
        hardness = row[25 - offset]
        sd_hv = row[26 - offset]
        measurements[composition_id][fabrication_method][batch][measurement_id][
            hardness_column
        ] = hardness
        measurements[composition_id][fabrication_method][batch][measurement_id][
            sd_hv_column
        ] = sd_hv

        # T08: elastic modulus, yield strength, uts, elongtation, strain hardnening
        measurement_id = row[27]
        elastic_modulus_column = column_names[27]
        yield_stength_column = column_names[28]
        uts_column = column_names[29]
        elongation_column = column_names[30]
        strain_hardening_column = column_names[31]
        derivative_column = column_names[32]
        derivative_column = derivative_column.replace("\u03c3", "d")

        elastic_modulus = row[28]
        yield_stength = row[29]
        uts = row[30]
        elongation = row[31]
        strain_hardening = row[32]
        derivative = row[33]

        measurements[composition_id][fabrication_method][batch][measurement_id][
            elastic_modulus_column
        ] = elastic_modulus
        measurements[composition_id][fabrication_method][batch][measurement_id][
            yield_stength_column
        ] = yield_stength
        measurements[composition_id][fabrication_method][batch][measurement_id][
            uts_column
        ] = uts
        measurements[composition_id][fabrication_method][batch][measurement_id][
            elongation_column
        ] = elongation
        measurements[composition_id][fabrication_method][batch][measurement_id][
            strain_hardening_column
        ] = strain_hardening
        measurements[composition_id][fabrication_method][batch][measurement_id][
            derivative_column
        ] = derivative

        # T09: elastic modulus, yield strength, uts, elongtation, strain hardnening
        measurement_id = row[34]
        elastic_modulus_column = column_names[34]
        yield_stength_column = column_names[35]
        uts_column = column_names[36]
        elongation_column = column_names[37]
        strain_hardening_column = column_names[38]
        derivative_column = column_names[39]
        derivative_column = derivative_column.replace("\u03c3", "d")

        elastic_modulus = row[35]
        yield_stength = row[36]
        uts = row[37]
        elongation = row[38]
        strain_hardening = row[39]
        derivative = row[40]

        measurements[composition_id][fabrication_method][batch][measurement_id][
            elastic_modulus_column
        ] = elastic_modulus
        measurements[composition_id][fabrication_method][batch][measurement_id][
            yield_stength_column
        ] = yield_stength
        measurements[composition_id][fabrication_method][batch][measurement_id][
            uts_column
        ] = uts
        measurements[composition_id][fabrication_method][batch][measurement_id][
            elongation_column
        ] = elongation
        measurements[composition_id][fabrication_method][batch][measurement_id][
            strain_hardening_column
        ] = strain_hardening
        measurements[composition_id][fabrication_method][batch][measurement_id][
            derivative_column
        ] = derivative

        # Average: elastic modulus, yield strength, uts, elongtation, strain hardnening
        measurement_id = row[41]
        elastic_modulus_column = column_names[41]
        yield_stength_column = column_names[42]
        uts_column = column_names[43]
        elongation_column = column_names[44]
        strain_hardening_column = column_names[45]
        derivative_column = column_names[46]
        derivative_column = derivative_column.replace("\u03c3", "d")

        elastic_modulus = row[42]
        yield_stength = row[43]
        uts = row[44]
        elongation = row[45]
        strain_hardening = row[46]
        derivative = row[47]

        measurements[composition_id][fabrication_method][batch][measurement_id][
            elastic_modulus_column
        ] = elastic_modulus
        measurements[composition_id][fabrication_method][batch][measurement_id][
            yield_stength_column
        ] = yield_stength
        measurements[composition_id][fabrication_method][batch][measurement_id][
            uts_column
        ] = uts
        measurements[composition_id][fabrication_method][batch][measurement_id][
            elongation_column
        ] = elongation
        measurements[composition_id][fabrication_method][batch][measurement_id][
            strain_hardening_column
        ] = strain_hardening
        measurements[composition_id][fabrication_method][batch][measurement_id][
            derivative_column
        ] = derivative

    strain_rate_and_temperature_df = df[19:21]
    strain_rate_and_temperature_df.columns = new_header


def ingest_srjt_results(srjt_path, output, measurements):
    # FIXME: add file link
    # Convert the Excel file to CSV using LibreOffice
    output_file = str(srjt_path).split(".")[0] + ".csv"
    output_file = output_file.split("/")[-1]

    conversion_command = [
        "libreoffice",
        "--headless",  # Run LibreOffice in headless mode (without GUI)
        "--convert-to",
        "csv",
        "--outdir",
        output,  # Output directory
        srjt_path,
    ]

    subprocess.run(conversion_command)

    # Read the CSV file into a Pandas DataFrame
    df = pd.read_csv(output / output_file)

    # Clean up the temporary CSV file
    subprocess.run(["rm", output / output_file])

    columns = list(df.columns)
    sample_name_column = list(filter(lambda x: "Sample Name" in x, columns))[0]

    for i in range(len(df)):
        composition_id = df.loc[i, sample_name_column]
        for y in range(2, len(columns)):
            # print(columns[y])
            measurements[composition_id]["SRJT"][columns[y]] = df.loc[i, columns[y]]
