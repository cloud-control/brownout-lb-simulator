function data = read_final_result_file(filepath)

tmp = readtable(filepath);

data.avgResponseTime = tmp.avgResponseTime;
data.cloneStdCoeff = tmp.cloneStdCoeff;
data.util = tmp.avgUtil;

end