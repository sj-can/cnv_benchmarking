import subprocess, sys

def cn_calculator(alt_list, genotype, X=False, Y=False):
    if X:
        print('x')
        cnv = False
        for i in genotype:
            if i == 0:
                pass
            else:
                print('cnv')
                return True
    if Y:
        print('Y')
        cnv = False
        for i in genotype:
            if i == 0:
                pass
            else:
                print('cnv')
                return True
    else:
        desired_cn = [0,1,3]
        cn_changed = False
        cn_count = 0
        for i in genotype:
            if i == '0':
                cn_count += 1
                cn_changed = True
            else:
                alt_index = int(i)-1
                cn = alt_list[alt_index]
                if int(cn.split('CN')[-1].strip('>')) == 0:
                    cn_changed = True
                else:
                    cn_count += int(cn.split('CN')[-1].strip('>'))
                    cn_changed = True
        if cn_count in desired_cn and cn_changed:
            #print("cn_count = " + str(cn_count))
            return cn_count

def parse_output_vcf(vcf_file, sample_id):
    with open(vcf_file, 'r') as inf:
        cn_counter = [0,0,0]
        length_array = [[],[],[]]
        x_count = 0
        y_count = 0
        for line in inf:
            spl = line.strip('\n').split('\t')
            if spl[-1] != "0|0" and spl[-1] != "0":
                try:
                    start = int(spl[1])
                    info = spl[7].split(';')
                    for i,j in enumerate(info):
                        if j.startswith("END="):
                            end = int(j.split("=")[-1])
                            length = end-start
                            if length >= 30000:
                                alt = spl[4].split(',')
                                gt = spl[-1].split('|')
                                if spl[0] == 'X':
                                    cnv = cn_calculator(alt, gt, X=True)
                                    if cnv:
                                        xcount += 1
                                elif spl[0] == 'Y':
                                    cnv = cn_calculator(alt, gt, Y=True)
                                    if cnv:
                                        ycount += 1
                                else:
                                    this_cn = cn_calculator(alt, gt)
                                    if this_cn == 0:
                                        cn_counter[0] += 1
                                        #lenght_array[0].append(length)
                                    elif this_cn == 1:
                                        cn_counter[1] += 1
                                        #length_array[1].append(length)
                                    elif this_cn == 3:
                                        cn_counter[2] += 1
                                        #length_array[2].append(length)
                except:
                    print(spl)
                    print( )
    with open("output_cnv_summary", 'a') as ouf:
        total_cn = sum(cn_counter)
        total_xy = total_cn + x_count + y_count
    	ouf.write(sample_id +'\t'+ str(total_cn) +'\t'+ str(total_xy) +'\t'+  str(cn_counter[0]) +'\t'+ str(cn_counter[1]) +'\t'+ str(cn_counter[2]) +'\t'+ str(x_count) +'\t'+ str(y_count) + '\n')
    subprocess.call(['rm', vcf_file])

def run_vcftools(vcf_file, sample_file):
    map_dict = {}
    with open(sample_file, 'r') as sample_f:
        for line in sample_f:
            sample_name = line.strip('\n')
            print(sample_name)
            out_file = "outputs/" + sample_name + ".sv.vcf"
            print(out_file)
            vcf_cmd = ["vcftools", "--vcf", vcf_file, "--indv", sample_name, "--recode", "--recode-INFO-all", "-c"]
            this_call = subprocess.Popen(vcf_cmd, stdout=subprocess.PIPE)
            filtered_vcf = this_call.communicate()[0]
            with open(out_file, "w") as ouf:
                ouf.write(filtered_vcf)
            map_dict_update = parse_output_vcf(out_file, sample_name)
            
if __name__ == "__main__":
    run_vcftools("ALL.wgs.integrated_sv_map_v2.20130502.svs.genotypes.vcf", "sample_list.1000g.svmap")

